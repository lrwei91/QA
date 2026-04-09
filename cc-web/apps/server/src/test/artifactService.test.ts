import fs from "node:fs";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import { createDatabase } from "../db/client.js";
import { ArtifactService } from "../services/artifactService.js";
import { createTestConfig } from "./helpers.js";

const cleanups: Array<() => Promise<void>> = [];

afterEach(async () => {
  while (cleanups.length > 0) {
    const cleanup = cleanups.pop();
    if (cleanup) {
      await cleanup();
    }
  }
});

describe("artifact service", () => {
  it("detects changed target conflicts", async () => {
    const fixture = await createTestConfig();
    cleanups.push(fixture.cleanup);
    const db = createDatabase(path.join(fixture.config.dataDir, "meta.sqlite"));
    const service = new ArtifactService(db, fixture.config);

    const artifactPath = path.join(fixture.config.dataDir, "artifact.xlsx");
    const publishTargetPath = path.join(fixture.config.sourceRepo, "testcases/generated/demo.xlsx");
    await fs.promises.writeFile(artifactPath, "new-content", "utf8");
    await fs.promises.writeFile(publishTargetPath, "old-content", "utf8");

    const preview = service.previewPublish([
      {
        id: "art_1",
        sessionId: "ses_1",
        runId: "run_1",
        relativePath: "testcases/generated/demo.xlsx",
        artifactPath,
        publishTargetPath,
        status: "ready",
        sizeBytes: 11,
        mimeType: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        checksum: "fake",
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        publishedAt: null,
      },
    ]);

    expect(preview.conflicts[0]?.exists).toBe(true);
    expect(preview.conflicts[0]?.changed).toBe(true);
    db.close();
  });
});
