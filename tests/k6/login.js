import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  scenarios: {
    login_load: {
      executor: "shared-iterations",
      vus: 20,
      iterations: 500,
      maxDuration: "60s",
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
  },
};

const loginUrl = __ENV.LOGIN_URL || "http://127.0.0.1:8001/login";

export default function () {
  const response = http.get(loginUrl, {
    tags: { name: "GET /login" },
  });

  check(response, {
    "GET /login returns 200": (result) => result.status === 200,
    "login form is rendered": (result) =>
      result.body.includes("Autentificare"),
  });

  sleep(1);
}
