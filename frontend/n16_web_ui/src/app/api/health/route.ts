import { env } from "@/lib/env";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export async function GET(request: Request) {
  const maxTimeMs = 180 * 1000; // 3 minutes
  const startTime = Date.now();
  let retryDelayMs = 1000;
  let attempt = 1;

  while (Date.now() - startTime < maxTimeMs) {
    try {
      const res = await fetch(`${env.BACKEND_URL}/health`, {
        method: "GET",
        headers: { "X-Internal-Key": env.INTERNAL_API_KEY },
        cache: "no-store",
        signal: request.signal
      });

      if (res.ok) {
        const data = await res.json();
        return Response.json(data);
      }

      console.warn(`[Health Check] Attempt ${attempt} failed with status: ${res.status}`);
      if (Date.now() - startTime >= maxTimeMs) {
        return Response.json({ status: "error" }, { status: res.status });
      }
    } catch (err: any) {
      if (request.signal.aborted || err?.name === "AbortError") {
        console.log(`[Health Check] Client aborted the request. Stopping retries.`);
        return new Response(null, { status: 499 });
      }
      console.error(`[Health Check] Attempt ${attempt} error:`, err?.message || err);
      if (Date.now() - startTime >= maxTimeMs) {
        return Response.json(
          { status: "error", message: err?.message || "Failed to fetch health" },
          { status: 502 },
        );
      }
    }
    await sleep(retryDelayMs);
    retryDelayMs = Math.min(retryDelayMs * 2, 10000); // Cap exponential backoff at 10s
    attempt++;
  }

  return Response.json({ status: "error", message: "Timeout" }, { status: 504 });
}
