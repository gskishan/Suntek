import { useState } from "react";

interface SalesOrder {
    name: string;
    customer: string;
    creation: string;
    type_of_case: string;
    status: string;
    grand_total: number;
}

interface SalesOrderItemProps {
    order: SalesOrder;
}

const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
        "To Deliver and Bill": "bg-yellow-100 text-yellow-800",
        Completed: "bg-green-100 text-green-800",
        Closed: "bg-gray-100 text-gray-800",
        Draft: "bg-blue-100 text-blue-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
};

const getTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
        Subsidy: "bg-purple-100 text-purple-800",
        "Non Subsidy": "bg-orange-100 text-orange-800",
    };
    return colors[type] || "bg-gray-100 text-gray-800";
};

export const SalesOrderItem = ({ order }: SalesOrderItemProps) => {
    const [isExpanded, setIsExpanded] = useState(false);

    return (
        <div className="bg-white rounded-lg p-3 hover:bg-gray-50 transition-colors">
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className="w-full text-left"
            >
                <div className="flex items-center justify-between">
                    <div>
                        <div className="font-medium text-gray-900">{order.name}</div>
                        <div className="text-sm text-gray-600">{order.customer}</div>
                    </div>
                    <div className="text-right">
                        <div className="font-medium text-gray-900">₹{order.grand_total.toLocaleString()}</div>
                        <div className="text-sm text-gray-600">{new Date(order.creation).toLocaleDateString()}</div>
                    </div>
                </div>
            </button>

            {isExpanded && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                    <div className="flex flex-wrap gap-2">
                        <span
                            className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}
                        >
                            {order.status}
                        </span>
                        <span
                            className={`px-2.5 py-1 rounded-full text-xs font-medium ${getTypeColor(order.type_of_case)}`}
                        >
                            {order.type_of_case || "Unspecified Type"}
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
};
