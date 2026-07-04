"use client";

import {useEffect, useState, useCallback} from "react";
import {api, APIError, Ticket} from "@/lib/api";
import {useLocalStorage} from "@/lib/hooks";
import {TicketForm} from "@/components/TicketForm";
import {LoginForm} from "@/components/LoginForm";
import {TicketTable} from "@/components/TicketTable";
import {FilterBar} from "@/components/FilterBar";
import {Pagination} from "@/components/Pagination";

export default function Home() {
    const [auth, setAuth, authLoaded] = useLocalStorage<{
        username: string;
        password: string;
        isAdmin: boolean;
    } | null>("auth", null);

    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isDeleting, setIsDeleting] = useState<Set<number>>(new Set());

    const [search, setSearch] = useState("");
    const [status, setStatus] = useState("");
    const [priority, setPriority] = useState("");
    const [sortBy, setSortBy] = useState("created_at");
    const [sortOrder, setSortOrder] = useState("desc");
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);

    const loadTickets = useCallback(async () => {
        try {
            setIsLoading(true);
            setError(null);
            const response = await api.getTickets({
                search: search || undefined,
                status: status || undefined,
                priority: priority || undefined,
                sort_by: sortBy,
                sort_order: sortOrder,
                page,
                page_size: 10,
            });
            setTickets(response.items);
            setTotalPages(response.total_pages);
        } catch (err) {
            console.log(err);
            const message = err instanceof APIError ? err.message : "Не удалось загрузить заявки";
            setError(message);
        } finally {
            setIsLoading(false);
        }
    }, [search, status, priority, sortBy, sortOrder, page]);

    useEffect(() => {
        loadTickets();
    }, [loadTickets]);

    const handleCreateTicket = async (data: {
        title: string;
        description?: string;
        priority: string;
    }) => {
        try {
            setError(null);
            await api.createTicket(data);
            setPage(1);
            await loadTickets();
        } catch (err) {
            const message = err instanceof APIError ? err.message : "Не удалось создать заявку";
            setError(message);
        }
    };

    const handleStatusChange = async (id: number, newStatus: string) => {
        try {
            setError(null);
            await api.updateTicketStatus(id, newStatus);
            await loadTickets();
        } catch (err) {
            const message = err instanceof APIError ? err.message : "Не удалось обновить заявку";
            setError(message);
        }
    };

    const handleDeleteTicket = async (id: number) => {
        if (!auth?.isAdmin) {
            setError("Для удаления требуются права администратора");
            return;
        }

        try {
            setError(null);
            setIsDeleting((prev) => new Set(prev).add(id));
            await api.deleteTicket(id, auth.username, auth.password);
            await loadTickets();
        } catch (err) {
            const message = err instanceof APIError ? err.message : "Не удалось удалить заявку";
            setError(message);
        } finally {
            setIsDeleting((prev) => {
                const next = new Set(prev);
                next.delete(id);
                return next;
            });
        }
    };

    const handleLogin = async (username: string, password: string) => {
        try {
            setError(null);
            const user = await api.getCurrentUser(username, password);
            if (user) {
                setAuth({username, password, isAdmin: user.is_admin});
            }
        } catch (err) {
            const message = err instanceof APIError ? err.message : "Вход не удался";
            setError(message);
        }
    };

    const handleLogout = () => {
        setAuth(null);
    };

    if (!authLoaded) {
        return <div className="loading-message">Загрузка...</div>;
    }

    return (
        <main className="app-container">
            <div className="app-header">
                <h1>Менеджер заявок</h1>
                {auth ? (
                    <button onClick={handleLogout} className="logout-btn">
                        Выйти ({auth.username})
                    </button>
                ) : (
                    <span className="login-status">Вы не вошли в аккаунт</span>
                )}
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="main-content">

                {!auth && (
                    <section className="login-section">
                        <h2>Вход</h2>
                        <LoginForm onLogin={handleLogin}/>
                    </section>
                )}

                <section className="create-section">
                    <h2>Создать новую заявку</h2>
                    <TicketForm onSubmit={handleCreateTicket} isLoading={isLoading}/>
                </section>

                <section className="tickets-section">
                    <h2>Заявки</h2>
                    <FilterBar
                        search={search}
                        onSearchChange={(value) => {
                            setSearch(value);
                            setPage(1);
                        }}
                        status={status}
                        onStatusChange={(value) => {
                            setStatus(value);
                            setPage(1);
                        }}
                        priority={priority}
                        onPriorityChange={(value) => {
                            setPriority(value);
                            setPage(1);
                        }}
                        sortBy={sortBy}
                        onSortByChange={setSortBy}
                        sortOrder={sortOrder}
                        onSortOrderChange={setSortOrder}
                        isLoading={isLoading}
                    />

                    <TicketTable
                        tickets={tickets}
                        isLoading={isLoading}
                        onStatusChange={handleStatusChange}
                        onDelete={handleDeleteTicket}
                        isAdmin={auth?.isAdmin}
                        isDeleting={isDeleting}
                    />

                    <Pagination
                        page={page}
                        totalPages={totalPages}
                        onPageChange={setPage}
                        isLoading={isLoading}
                    />
                </section>
            </div>
        </main>
    );
}
