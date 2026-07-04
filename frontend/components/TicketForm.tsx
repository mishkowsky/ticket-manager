"use client";

import React, {useState} from "react";

interface TicketFormProps {
    onSubmit: (data: { title: string; description?: string; priority: string }) => void;
    isLoading?: boolean;
}

export function TicketForm({onSubmit, isLoading}: TicketFormProps) {
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [priority, setPriority] = useState("normal");

    const handleSubmit = (e: React.SubmitEvent) => {
        e.preventDefault();
        onSubmit({title, description: description || undefined, priority});
        setTitle("");
        setDescription("");
        setPriority("normal");
    };

    return (
        <form onSubmit={handleSubmit} className="ticket-form">
            <div className="form-group">
                <label htmlFor="title">Заголовок *</label>
                <input
                    id="title"
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    disabled={isLoading}
                    minLength={3}
                    maxLength={120}
                    required
                    placeholder="Введите название заявки"
                />
            </div>
            <div className="form-group">
                <label htmlFor="description">Описание</label>
                <textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    disabled={isLoading}
                    maxLength={1000}
                    placeholder="Введите описание заявки (необязательно)"
                    rows={3}
                />
            </div>
            <div className="form-group">
                <label htmlFor="priority">Приоритет</label>
                <select
                    id="priority"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    disabled={isLoading}
                >
                    <option value="low">Низкий</option>
                    <option value="normal">Средний</option>
                    <option value="high">Высокий</option>
                </select>
            </div>
            <button type="submit" disabled={isLoading}>
                {isLoading ? "Создание..." : "Создать заявку"}
            </button>
        </form>
    );
}
