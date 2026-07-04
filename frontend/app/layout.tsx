import type {Metadata} from "next";
import "./globals.css";
import React from "react";

export const metadata: Metadata = {
    title: "Менеджер заявок",
    description: "Небольшое веб-приложение для учёта внутренних заявок.",
};

export default function RootLayout({children}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="ru">
        <body>{children}</body>
        </html>
    );
}
