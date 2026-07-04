"use client";

interface FilterBarProps {
    search: string;
    onSearchChange: (value: string) => void;
    status: string;
    onStatusChange: (value: string) => void;
    priority: string;
    onPriorityChange: (value: string) => void;
    sortBy: string;
    onSortByChange: (value: string) => void;
    sortOrder: string;
    onSortOrderChange: (value: string) => void;
    isLoading?: boolean;
}

export function FilterBar({
                              search, onSearchChange, status, onStatusChange, priority, onPriorityChange,
                              sortBy, onSortByChange, sortOrder, onSortOrderChange, isLoading,
                          }: FilterBarProps) {
    return (
        <div>
            <div className="filter-bar">
                <div className="filter-group">
                    <input
                        type="text"
                        placeholder="Поиск по заголовку или описанию..."
                        value={search}
                        onChange={(e) => onSearchChange(e.target.value)}
                        disabled={isLoading}
                        className="search-input"
                    />
                </div>
            </div>
            <div className="filter-bar">
                <div className="filter-group">
                    <label htmlFor="status-filter">Статус</label>
                    <select
                        id="status-filter"
                        value={status}
                        onChange={(e) => onStatusChange(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="">Все</option>
                        <option value="new">Новая</option>
                        <option value="in_progress">В работе</option>
                        <option value="done">Выполнена</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label htmlFor="priority-filter">Приоритет</label>
                    <select
                        id="priority-filter"
                        value={priority}
                        onChange={(e) => onPriorityChange(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="">Все</option>
                        <option value="low">Низкий</option>
                        <option value="normal">Средний</option>
                        <option value="high">Высокий</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label htmlFor="sort-by">Сортировать по</label>
                    <select
                        id="sort-by"
                        value={sortBy}
                        onChange={(e) => onSortByChange(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="created_at">Дата создания</option>
                        <option value="priority">Проиритет</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label htmlFor="sort-order">Порядок сортировки</label>
                    <select
                        id="sort-order"
                        value={sortOrder}
                        onChange={(e) => onSortOrderChange(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="desc">Убывающий</option>
                        <option value="asc">Возрастающий</option>
                    </select>
                </div>
            </div>
        </div>
    );
}
