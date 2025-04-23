import { TableCell, TableRow } from "@/components/ui/table";
import { ChevronDown, ChevronRight, ExternalLink } from "lucide-react";
import { SalesOrderRowProps } from "./types";

export const OrderRow = ({
    order,
    expanded,
    toggleExpanded,
    formatCurrency,
    formatDate,
    getStatusColor,
    getTypeColor,
    getERPUrl,
    getDepartmentAcronym,
    getDepartmentColor,
}: SalesOrderRowProps) => {
    return (
        <>
            <TableRow className="bg-muted/10 hover:bg-muted/20">
                <TableCell className="pl-20">
                    <div
                        className="flex items-center w-full cursor-pointer"
                        onClick={toggleExpanded}
                    >
                        {expanded ? (
                            <ChevronDown className="h-4 w-4 mr-2 text-gray-500" />
                        ) : (
                            <ChevronRight className="h-4 w-4 mr-2 text-gray-500" />
                        )}
                        <div>
                            <div className="flex items-center">
                                <a
                                    href={getERPUrl("Sales Order", order.name)}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                                    onClick={(e) => e.stopPropagation()}
                                >
                                    {order.name}
                                </a>
                                <ExternalLink className="h-3 w-3 ml-1 text-gray-400" />
                            </div>
                            <div className="text-sm text-gray-600 mt-0.5">{order.customer}</div>
                        </div>
                    </div>
                </TableCell>
                <TableCell colSpan={2}>
                    <div className="flex flex-wrap gap-2">
                        <span
                            className={`px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}
                        >
                            {order.status}
                        </span>
                        <span
                            className={`px-2.5 py-1 rounded-full text-xs font-medium ${getTypeColor(
                                order.type_of_case,
                            )}`}
                        >
                            {order.type_of_case || "Unspecified Type"}
                        </span>
                    </div>
                </TableCell>
                <TableCell>
                    <span className="font-medium">₹{formatCurrency(order.grand_total)}</span>
                </TableCell>
                <TableCell colSpan={2}>
                    <div className="text-gray-600">{formatDate(order.creation)}</div>
                </TableCell>
            </TableRow>

            {expanded && (
                <TableRow className="bg-muted/5">
                    <TableCell
                        colSpan={6}
                        className="p-3 pl-24"
                    >
                        <div className="grid grid-cols-3 gap-4 text-sm">
                            <div>
                                <div className="text-gray-500 mb-1">Creation Date:</div>
                                <div>{new Date(order.creation).toLocaleString()}</div>
                            </div>
                            {order.capacity_value && (
                                <div>
                                    <div className="text-gray-500 mb-1">Capacity:</div>
                                    <div>
                                        {order.capacity_raw} ({order.capacity_value} kW)
                                    </div>
                                </div>
                            )}
                            {order.type_of_structure && (
                                <div>
                                    <div className="text-gray-500 mb-1">Structure Type:</div>
                                    <div>{order.type_of_structure}</div>
                                </div>
                            )}
                            {order.sales_person && (
                                <div>
                                    <div className="text-gray-500 mb-1">Sales Person:</div>
                                    <div>{order.sales_person}</div>
                                </div>
                            )}
                        </div>
                    </TableCell>
                </TableRow>
            )}
        </>
    );
};
