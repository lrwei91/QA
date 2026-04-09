import { z } from "zod";
import type { FastifyInstance } from "fastify";

const loginSchema = z.object({
  username: z.string().trim().min(1),
  password: z.string().min(1),
});

export async function registerAuthRoutes(app: FastifyInstance) {
  app.post("/api/auth/login", async (request, reply) => {
    const payload = loginSchema.parse(request.body);
    const user = app.userService.authenticate(payload.username, payload.password);
    if (!user) {
      return reply.code(401).send({ message: "用户名或密码错误" });
    }

    const token = await reply.jwtSign(
      {
        sub: user.id,
        username: user.username,
        role: user.role,
      },
      {
        sign: {
          expiresIn: "7d",
        },
      },
    );
    reply.setCookie("cc_web_token", token, {
      httpOnly: true,
      sameSite: "lax",
      path: "/",
      secure: false,
    });
    return { user };
  });

  app.get("/api/auth/me", { preHandler: [app.authenticate] }, async (request) => {
    return { user: request.currentUser };
  });

  app.post("/api/auth/logout", async (_request, reply) => {
    reply.clearCookie("cc_web_token", {
      path: "/",
      httpOnly: true,
      sameSite: "lax",
      secure: false,
    });
    return { ok: true };
  });
}
