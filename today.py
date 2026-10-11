"""
Busca estatísticas na API GraphQL do GitHub, salva em stats.json e
regenera os SVGs. Roda diariamente via GitHub Actions.

Variáveis de ambiente:
    ACCESS_TOKEN  token pessoal (fine-grained, só leitura)
    USER_NAME     seu usuário (padrão: mmarqueti)
"""
import json
import os
from datetime import datetime, timezone

import requests

import render

TOKEN = os.environ["ACCESS_TOKEN"]
USER = os.environ.get("USER_NAME", "mmarqueti")
API = "https://api.github.com/graphql"


def gql(query, variables=None):
    r = requests.post(API, json={"query": query, "variables": variables or {}},
                      headers={"Authorization": f"bearer {TOKEN}"}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def main():
    base = gql("""
    query($login: String!) {
      user(login: $login) {
        createdAt
        followers { totalCount }
        repositories(ownerAffiliations: OWNER) { totalCount }
        repositoriesContributedTo(contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY], includeUserRepositories: true) { totalCount }
      }
    }""", {"login": USER})["user"]

    # estrelas: soma de todos os repositórios próprios (paginado)
    stars, cursor = 0, None
    while True:
        page = gql("""
        query($login: String!, $cursor: String) {
          user(login: $login) {
            repositories(first: 100, after: $cursor, ownerAffiliations: OWNER) {
              pageInfo { hasNextPage endCursor }
              nodes { stargazerCount }
            }
          }
        }""", {"login": USER, "cursor": cursor})["user"]["repositories"]
        stars += sum(n["stargazerCount"] for n in page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    # commits: soma ano a ano desde a criação da conta
    created = datetime.fromisoformat(base["createdAt"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    commits = 0
    for year in range(created.year, now.year + 1):
        start = max(created, datetime(year, 1, 1, tzinfo=timezone.utc))
        end = min(now, datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        c = gql("""
        query($login: String!, $from: DateTime!, $to: DateTime!) {
          user(login: $login) {
            contributionsCollection(from: $from, to: $to) {
              totalCommitContributions
              restrictedContributionsCount
            }
          }
        }""", {"login": USER, "from": start.isoformat(), "to": end.isoformat()})
        cc = c["user"]["contributionsCollection"]
        commits += cc["totalCommitContributions"]

    stats = {
        "repos": base["repositories"]["totalCount"],
        "contributed": base["repositoriesContributedTo"]["totalCount"],
        "stars": stars,
        "commits": commits,
        "followers": base["followers"]["totalCount"],
        "updated": now.strftime("%Y-%m-%d"),
    }
    with open(os.path.join(render.HERE, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    print(stats)
    render.build()


if __name__ == "__main__":
    main()
