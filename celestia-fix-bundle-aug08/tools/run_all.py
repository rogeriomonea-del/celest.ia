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
        try:
            res = await run_priority_sources(o, d, dt)
        except Exception as e:
            print("Runner error:", e)
            continue
        if not res:
            print("No results (yet).")
        else:
            best = sorted(res, key=lambda x: x.get("price", 1e12))[:3]
            for i, it in enumerate(best, 1):
                print(f"{i}) {it}")
        print()

if __name__ == "__main__":
    asyncio.run(main())
