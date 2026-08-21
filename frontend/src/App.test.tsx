import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { App } from "./App";

describe("TopHouse App", () => {
  it("muestra la portada y navega al catálogo", async () => {
    const user = userEvent.setup();
    render(<App />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Tu próximo lugar",
    );
    await user.click(
      screen.getByRole("link", { name: "Explorar propiedades" }),
    );
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Propiedades para tu próxima etapa",
    );
  });
});
