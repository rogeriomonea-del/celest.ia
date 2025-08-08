import asyncio
from services.orchestrator_bandit import run_priority_sources

ROUTES = [
    ("GRU","MCO","2025-09-01"),
    ("CGH","SDU","2025-09-01"),
    ("GRU","LIS","2025-09-01"),
]

async def main():
    for o, d, dt in ROUTES:
        print(f"=== Running {o}->{d} on {dt} ===")
        res = await run_priority_sources(o, d, dt)
        if not res:
            print("No results found (yet).")
        else:
            # print best 3
            best = sorted(res, key=lambda x: x.get("price", 1e12))[:3]
            for i, it in enumerate(best, 1):
                print(f"{i}) {it}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
