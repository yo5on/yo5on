import { next, rewrite } from "@vercel/functions";

export const config = {
  matcher: ["/stats\\.svg$", "/streak\\.svg$"],
};

const graphics: Record<string, string> = {
  "/stats.svg": "stats",
  "/streak.svg": "streak",
};

export default function middleware(request: Request) {
  const url = new URL(request.url);
  const graphic = graphics[url.pathname];

  if (!graphic) return next();

  url.pathname = "/api/contributions";
  url.searchParams.set("graphic", graphic);
  return rewrite(url);
}
