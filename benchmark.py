"""
Task 3: Model benchmarking script.
Tests all configured models on a standard set of prompts and reports
accuracy, latency, and availability.
"""
import sys
import time
import json
import os
sys.stdout.reconfigure(encoding="utf-8")
from datetime import datetime
from typing import Optional
from llm_provider import LLMProvider
from langchain_core.messages import HumanMessage

# ─── Benchmark test cases ─────────────────────────────────────────────────────

BENCHMARKS = [
    {
        "id": "math",
        "prompt": "What is 17 * 83? Reply with only the number.",
        "expected": "1411",
        "type": "exact",
    },
    {
        "id": "reasoning",
        "prompt": "If a train travels 60 mph for 2.5 hours, how far does it go? Reply with only the number in miles.",
        "expected": "150",
        "type": "exact",
    },
    {
        "id": "factual",
        "prompt": "What is the capital of Japan? Reply with one word.",
        "expected": "tokyo",
        "type": "contains",
    },
    {
        "id": "coding",
        "prompt": "Write a Python one-liner to reverse a string s. Reply with only the code.",
        "expected": "[::-1]",
        "type": "contains",
    },
    {
        "id": "language",
        "prompt": "Translate 'Hello, how are you?' to Spanish. Reply with only the translation.",
        "expected": "hola",
        "type": "contains",
    },
]

GOOGLE_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]


def check_answer(response: str, expected: str, check_type: str) -> bool:
    r = response.strip().lower()
    e = expected.strip().lower()
    if check_type == "exact":
        return e in r
    elif check_type == "contains":
        return e in r
    return False


def benchmark_model(provider: str, model: str) -> dict:
    """Run all benchmarks against one model. Returns results dict."""
    results = {
        "provider": provider,
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "available": False,
        "tests": [],
        "passed": 0,
        "total": len(BENCHMARKS),
        "avg_latency_ms": 0,
    }

    # Check if available
    try:
        llm = LLMProvider.get_llm(provider=provider, model=model, temperature=0.0)
        llm.invoke([HumanMessage(content="ping")])
        results["available"] = True
    except Exception as e:
        results["error"] = str(e)[:120]
        return results

    latencies = []
    for test in BENCHMARKS:
        start = time.time()
        try:
            resp = llm.invoke([HumanMessage(content=test["prompt"])])
            content = resp.content if isinstance(resp.content, str) else str(resp.content)
            elapsed_ms = (time.time() - start) * 1000
            passed = check_answer(content, test["expected"], test["type"])
            latencies.append(elapsed_ms)
            results["tests"].append({
                "id": test["id"],
                "passed": passed,
                "latency_ms": round(elapsed_ms),
                "response": content.strip()[:80],
            })
            if passed:
                results["passed"] += 1
            status = "PASS" if passed else "FAIL"
            print(f"    [{status}] {test['id']:12s} {elapsed_ms:6.0f}ms  {content.strip()[:50]}")
        except Exception as e:
            elapsed_ms = (time.time() - start) * 1000
            err = str(e)[:80]
            results["tests"].append({"id": test["id"], "passed": False, "error": err})
            print(f"    [ERR ] {test['id']:12s} {err[:50]}")

    if latencies:
        results["avg_latency_ms"] = round(sum(latencies) / len(latencies))

    return results


def run_benchmark(
    provider: Optional[str] = None,
    models: Optional[list] = None,
    save: bool = True,
) -> list:
    """
    Run benchmarks across models and print a summary table.

    Args:
        provider: 'google', 'openai', or 'anthropic'
        models: list of model names to test (uses defaults if None)
        save: save results to ./data/benchmark_results.json
    """
    from config import settings
    provider = provider or settings.default_llm_provider

    if models is None:
        if provider == "google":
            models = GOOGLE_MODELS
        elif provider == "openai":
            models = ["gpt-4o-mini", "gpt-3.5-turbo"]
        elif provider == "anthropic":
            models = ["claude-3-5-haiku-20241022", "claude-3-haiku-20240307"]
        else:
            models = []

    print(f"\n{'='*60}")
    print(f"  MODEL BENCHMARK  |  Provider: {provider}")
    print(f"{'='*60}")
    print(f"  Tests: {len(BENCHMARKS)} | Models: {len(models)}\n")

    all_results = []
    for model in models:
        print(f"\n  Model: {model}")
        result = benchmark_model(provider, model)
        all_results.append(result)
        if not result["available"]:
            print(f"    SKIPPED: {result.get('error','unavailable')[:60]}")

    # Summary table
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  {'Model':<30} {'Score':>7} {'Latency':>10} {'Status'}")
    print(f"  {'-'*58}")
    for r in all_results:
        if r["available"]:
            score = f"{r['passed']}/{r['total']}"
            latency = f"{r['avg_latency_ms']}ms"
            status = "OK"
        else:
            score = "-/-"
            latency = "-"
            status = "UNAVAILABLE"
        print(f"  {r['model']:<30} {score:>7} {latency:>10}   {status}")
    print(f"{'='*60}\n")

    # Save results
    if save:
        os.makedirs("./data", exist_ok=True)
        out = "./data/benchmark_results.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
        print(f"  Results saved to {out}\n")

    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Benchmark AI models")
    parser.add_argument("--provider", default=None, help="openai | anthropic | google")
    parser.add_argument("--models", nargs="*", help="Specific models to test")
    args = parser.parse_args()
    run_benchmark(provider=args.provider, models=args.models)
