"use client";

import {Ticket} from "@/lib/api";

interface TicketTableProps {
    tickets: Ticket[];
    isLoading?: boolean;
    onStatusChange: (id: number, status: string) => void;
    onDelete: (id: number) => void;
    isAdmin?: boolean;
    isDeleting?: Set<number>;
}

export function TicketTable({
                                tickets, isLoading, onStatusChange,
                                onDelete, isAdmin, isDeleting
                            }: TicketTableProps) {

    if (isLoading) {
        return <div className="loading-message">Загрузка заявок...</div>;
    }

    if (tickets.length === 0) {
        return <div className="empty-message">Заявок не найдено</div>;
    }

    const getPriorityDisplayName = (priority: string) => {
        switch (priority) {
            case "low":
                return "Низкий";
            case "normal":
                return "Средний";
            case "high":
                return "Высокий";
            default:
                return priority;
        }
    };

    const formatDate = (date: string) => {
        return new Date(date).toLocaleDateString("ru-RU", {
            year: "numeric",
            month: "short",
            day: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        });
    };

    return (
        <div className="table-wrapper">
            <table className="tickets-table">
                <thead>
                <tr>
                    <th>ID</th>
                    <th>Заголовок</th>
                    <th>Описание</th>
                    <th>Статус</th>
                    <th>Приоритет</th>
                    <th>Дата создания</th>
                    {isAdmin && <th>Действия</th>}
                </tr>
                </thead>
                <tbody>
                {tickets.map((ticket) => (
                    <tr key={ticket.id} className="ticket-row">
                        <td>{ticket.id}</td>
                        <td className="title-cell">{ticket.title}</td>
                        <td className="description-cell">{ticket.description || "-"}</td>
                        <td>
                            <select
                                value={ticket.status}
                                onChange={(e) => onStatusChange(ticket.id, e.target.value)}
                                disabled={ticket.status === "done"}
                            >
                                <option value="new">Новая</option>
                                <option value="in_progress">В работе</option>
                                <option value="done">Выполнена</option>
                            </select>
                        </td>
                        <td>
                <span>
                  {getPriorityDisplayName(ticket.priority)}
                </span>
                        </td>
                        <td className="date-cell">{formatDate(ticket.created_at)}</td>
                        {isAdmin && (
                            <td className="actions-cell">
                                <button
                                    onClick={() => onDelete(ticket.id)}
                                    disabled={isDeleting?.has(ticket.id) || ticket.status === "done"}
                                    className="delete-btn"
                                >
                                    {isDeleting?.has(ticket.id) ? "Удаление..." : "Удалить"}
                                </button>
                            </td>
                        )}
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}
