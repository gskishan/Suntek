import { useEffect, useRef, useState } from "react";
import { Table, TableCell, TableRow, TableBody, TableHead, TableHeader } from "@/components/ui/table";
import { ChevronRight, ChevronLeft, ChevronsLeft, ChevronsRight, ExternalLink } from "lucide-react";
import { Battery, Coins, Package, TrendingUp } from "lucide-react";
import { DepartmentRowProps, SalesOrder } from "./types";
import { TableCellMetric } from "./TableCellMetric";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { OrderDetailsModal } from "./OrderDetailsModal";
import { StatCell } from "./StatCell";

export const DepartmentRow = ({
    departmentData,
    departmentIndex,
    getLocationName,
    formatCurrency,
    formatDate,
    calculateAverage,
    createUniqueKey,
    getStatusColor,
    getTypeColor,
    registerRow,
    isFullExpansion,
    getERPUrl,
    getDepartmentAcronym,
    getDepartmentColor,
}: DepartmentRowProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);
    const ordersPerPage = 20;

    const totalPages = Math.ceil(departmentData.orders.length / ordersPerPage);
    const indexOfLastOrder = currentPage * ordersPerPage;
    const indexOfFirstOrder = indexOfLastOrder - ordersPerPage;
    const currentOrders = departmentData.orders.slice(indexOfFirstOrder, indexOfLastOrder);

    const rowKey = createUniqueKey(departmentData.department, "department", departmentIndex);

    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

    useEffect(() => {
        if (isFullExpansion) {
            setIsOpen(true);
        }
    }, [isFullExpansion]);

    const activeOrdersCount = departmentData.count - (departmentData.inactive_count || 0);

    const previousPage = () => {
        setCurrentPage((prev) => Math.max(1, prev - 1));
    };

    const nextPage = () => {
        setCurrentPage((prev) => Math.min(totalPages, prev + 1));
    };

    const firstPage = () => {
        setCurrentPage(1);
    };

    const lastPage = () => {
        setCurrentPage(totalPages);
    };

    const handleOrderClick = (order: SalesOrder) => {
        setSelectedOrder(order);
    };

    const closeOrderDetails = () => {
        setSelectedOrder(null);
    };

    return (
        <>
            <TableRow
                data-slot="table-row"
                className="data-[state=selected]:bg-muted border-b transition-colors hover:bg-muted/50 h-10"
            >
                <TableCell
                    data-slot="table-cell"
                    className="p-2 align-middle whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px] w-[300px] pl-12"
                >
                    <div
                        className="flex items-center justify-start w-full h-full cursor-pointer"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        <ChevronRight
                            className={`h-4 w-4 mr-2 inline transition-transform duration-300 ease-in-out ${isOpen ? "rotate-90" : "rotate-0"}`}
                        />
                        <span
                            className={`px-2 py-0.5 rounded text-xs font-medium ${getDepartmentColor(departmentData.department)}`}
                        >
                            {getLocationName(departmentData.department, "department")}
                        </span>
                    </div>
                </TableCell>
                <StatCell
                    icon={Package}
                    value={departmentData.count}
                    tooltip={`Total number of orders in ${getLocationName(departmentData.department, "department")}`}
                />
                <StatCell
                    icon={Package}
                    value={departmentData.inactive_count || 0}
                    tooltip={`Number of draft and cancelled orders in ${getLocationName(departmentData.department, "department")}`}
                />
                <StatCell
                    icon={Coins}
                    value={formatCurrency(departmentData.total_amount)}
                    width="w-[150px]"
                    tooltip={`Total revenue from all orders in ${getLocationName(departmentData.department, "department")}`}
                />
                <StatCell
                    icon={TrendingUp}
                    value={formatCurrency(calculateAverage(departmentData.total_amount, activeOrdersCount))}
                    tooltip={`Average order value in ${getLocationName(departmentData.department, "department")}`}
                />
                <StatCell
                    icon={Battery}
                    value={`${(departmentData.total_capacity || 0).toFixed(2)} kW`}
                    tooltip={`Total capacity in ${getLocationName(departmentData.department, "department")}`}
                />
            </TableRow>

            <TableRow
                className={`transition-all duration-300 ease-in-out overflow-hidden ${isOpen ? "opacity-100" : "opacity-0 h-0"}`}
            >
                <TableCell
                    colSpan={6}
                    className={`p-0 ${!isOpen ? "py-0" : ""}`}
                >
                    <div
                        className={`overflow-hidden transition-all duration-300 ease-in-out ${isOpen ? "max-h-[5000px]" : "max-h-0"}`}
                    >
                        <div className="border-t border-b border-gray-200 bg-gray-50/50 py-2">
                            {departmentData.orders.length > 0 ? (
                                <div className="px-10 mx-auto overflow-x-auto">
                                    <Table className="w-full table-fixed">
                                        <TableHeader className="bg-muted/20">
                                            <TableRow>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[14%]">
                                                    Order ID
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[13%]">
                                                    Customer
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[10%]">
                                                    Amount
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[10%]">
                                                    Sales Person
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[7%]">
                                                    Capacity
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[10%]">
                                                    Structure
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[10%]">
                                                    Date
                                                </TableHead>
                                                <TableHead className="font-medium text-xs h-8 py-1 w-[26%] text-right">
                                                    Details
                                                </TableHead>
                                            </TableRow>
                                        </TableHeader>
                                        <TableBody>
                                            {currentOrders.map((order, orderIndex) => (
                                                <TableRow
                                                    key={`order-${order.name}-${orderIndex}`}
                                                    className="hover:bg-muted/50 cursor-pointer"
                                                    onClick={() => handleOrderClick(order)}
                                                >
                                                    <TableCell
                                                        className="py-2 text-sm font-medium text-primary truncate"
                                                        title={order.name}
                                                    >
                                                        {order.name}
                                                    </TableCell>
                                                    <TableCell
                                                        className="py-2 text-sm truncate"
                                                        title={order.customer}
                                                    >
                                                        {order.customer.length > 17
                                                            ? order.customer.substring(0, 17) + "..."
                                                            : order.customer}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-sm whitespace-nowrap">
                                                        {formatCurrency(order.grand_total)}
                                                    </TableCell>
                                                    <TableCell
                                                        className="py-2 text-sm whitespace-nowrap"
                                                        title={order.sales_person || "No sales person assigned"}
                                                    >
                                                        {order.sales_person
                                                            ? order.sales_person.length > 10
                                                                ? order.sales_person.substring(0, 10) + "..."
                                                                : order.sales_person
                                                            : "-"}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-sm">
                                                        {order.capacity_value ? `${order.capacity_value} kW` : "-"}
                                                    </TableCell>
                                                    <TableCell
                                                        className="py-2 text-sm"
                                                        title={order.type_of_structure || "Not specified"}
                                                    >
                                                        {order.type_of_structure
                                                            ? order.type_of_structure.length > 10
                                                                ? order.type_of_structure.substring(0, 10) + "..."
                                                                : order.type_of_structure
                                                            : "-"}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-sm">
                                                        {formatDate(order.creation)}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-right">
                                                        <div className="flex justify-end items-center gap-2">
                                                            <Badge
                                                                className={`${getStatusColor(order.status)} text-[10px] py-0.5 px-2`}
                                                            >
                                                                {order.status}
                                                            </Badge>
                                                            <Badge
                                                                className={`${getTypeColor(order.type_of_case)} text-[10px] py-0.5 px-2`}
                                                            >
                                                                {order.type_of_case || "No Type"}
                                                            </Badge>
                                                            <a
                                                                href={`${getERPUrl("Sales Order", order.name)}`}
                                                                target="_blank"
                                                                rel="noopener noreferrer"
                                                                className="flex items-center text-xs text-primary hover:text-primary/80"
                                                                onClick={(e) => e.stopPropagation()}
                                                            >
                                                                <ExternalLink className="h-3 w-3 ml-1" />
                                                            </a>
                                                        </div>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>

                                    {totalPages > 1 && (
                                        <div className="flex justify-center mt-4 space-x-2">
                                            <Button
                                                variant="outline"
                                                size="icon"
                                                onClick={firstPage}
                                                disabled={currentPage === 1}
                                                className="h-8 w-8"
                                            >
                                                <ChevronsLeft className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="icon"
                                                onClick={previousPage}
                                                disabled={currentPage === 1}
                                                className="h-8 w-8"
                                            >
                                                <ChevronLeft className="h-4 w-4" />
                                            </Button>
                                            <span className="text-sm flex items-center px-2">
                                                Page {currentPage} of {totalPages}
                                            </span>
                                            <Button
                                                variant="outline"
                                                size="icon"
                                                onClick={nextPage}
                                                disabled={currentPage === totalPages}
                                                className="h-8 w-8"
                                            >
                                                <ChevronRight className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="outline"
                                                size="icon"
                                                onClick={lastPage}
                                                disabled={currentPage === totalPages}
                                                className="h-8 w-8"
                                            >
                                                <ChevronsRight className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="py-4 text-center text-sm text-gray-500">
                                    No orders found for this department.
                                </div>
                            )}
                        </div>
                    </div>
                </TableCell>
            </TableRow>

            {selectedOrder && (
                <OrderDetailsModal
                    selectedOrder={selectedOrder}
                    closeOrderDetails={closeOrderDetails}
                    formatCurrency={formatCurrency}
                    formatDate={formatDate}
                    getStatusColor={getStatusColor}
                    getTypeColor={getTypeColor}
                    getERPUrl={() => getERPUrl("Sales Order", selectedOrder.name)}
                />
            )}
        </>
    );
};
