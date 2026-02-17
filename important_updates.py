import hashlib
import itertools
import json
import sys
import networkx
from pathlib import Path

import spack.repo
import urllib.request

API_URL = "https://repology.org/api/v1/projects"
CACHE_DIR = Path(".cache")
USER_AGENT = "SpackBot/1.0"

graph: networkx.DiGraph = networkx.DiGraph()


def fetch_outdated_spack_projects():
    CACHE_DIR.mkdir(exist_ok=True)
    url = f"{API_URL}/?inrepo=spack&outdated=1"
    # name -> (our version, latest version seen in repology)
    projects: dict[str, tuple[str, str]] = {}
    at_least_per_page = 5
    while True:
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        cache_file = CACHE_DIR / f"{url_hash}.json"

        if cache_file.exists():
            print(f"Cache: {url}...", file=sys.stderr)
            with cache_file.open() as f:
                data = json.load(f)
        else:
            print(f"Fetch: {url}...", file=sys.stderr)
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request) as response:
                data = json.loads(response.read())
            with cache_file.open("w") as f:
                json.dump(data, f)
        last_project = ""
        for last_project, repos in data.items():
            spack_name = ""
            spack_version = ""
            max_version = "unknown"
            for repo in repos:
                if repo["status"] == "newest":
                    try:
                        max_version = repo["version"]
                    except Exception:
                        pass
                if repo["repo"] == "spack":
                    spack_version = repo["version"]
                    spack_name = repo["srcname"]
            if spack_name and spack_version:
                projects[spack_name] = (spack_version, max_version)
        if not last_project or len(data) < at_least_per_page:
            break
        url = f"{API_URL}/{last_project}/?inrepo=spack&outdated=1"
    return projects


def important_outdated_spack_projects():
    oudated = fetch_outdated_spack_projects()

    for pkg in spack.repo.PATH.all_package_classes():
        deps = itertools.chain.from_iterable(pkg.dependencies.values())
        for dep in deps:
            if spack.repo.PATH.is_virtual(dep):
                for provider in spack.repo.PATH.providers_for(dep):
                    graph.add_edge(pkg.name, provider.name)
            else:
                graph.add_edge(pkg.name, dep)

    _, authorities = networkx.hits(graph)

    authorities = sorted(authorities.items(), key=lambda x: x[1], reverse=True)
    authorities = [pkg for pkg, _ in authorities if pkg in oudated][:50]
    
    # Compute dynamic widths
    pkg_width = max(len(pkg) for pkg in authorities) if authorities else 0
    from_width = max(len(oudated[pkg][0]) for pkg in authorities) if authorities else 0
    to_width = max(len(oudated[pkg][1]) for pkg in authorities) if authorities else 0
    
    for pkg in authorities:
        print(f"{pkg:>{pkg_width}}: {oudated[pkg][0]:>{from_width}} -> {oudated[pkg][1]:<{to_width}}")


if __name__ == "__main__":
    important_outdated_spack_projects()
