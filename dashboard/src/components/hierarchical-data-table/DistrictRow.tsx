import { useEffect, useRef, useState } from "react";
import { Table, TableCell, TableRow, TableBody, TableHead, TableHeader } from "@/components/ui/table";
import { ChevronRight, ChevronLeft, ChevronsLeft, ChevronsRight } from "lucide-react";
import { Battery, Coins, Package, TrendingUp } from "lucide-react";
import { DistrictRowProps, SalesOrder } from "./types";
import { TableCellMetric } from "./TableCellMetric";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { OrderDetailsModal } from "./OrderDetailsModal";

export const DistrictRow = ({
    districtData,
    districtIndex,
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
}: DistrictRowProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const ordersPerPage = 20;

    const totalPages = Math.ceil(districtData.orders.length / ordersPerPage);

    const indexOfLastOrder = currentPage * ordersPerPage;
    const indexOfFirstOrder = indexOfLastOrder - ordersPerPage;
    const currentOrders = districtData.orders.slice(indexOfFirstOrder, indexOfLastOrder);

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

    const rowKey = createUniqueKey(districtData.district, "district", districtIndex);

    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

    useEffect(() => {
        if (isFullExpansion) {
            setIsOpen(true);
        }
    }, [isFullExpansion]);

    const [selectedOrder, setSelectedOrder] = useState<SalesOrder | null>(null);

    const handleOrderClick = (order: SalesOrder) => {
        setSelectedOrder(order);
    };

    const closeOrderDetails = () => {
        setSelectedOrder(null);
    };

    const activeOrdersCount = districtData.count - (districtData.inactive_count || 0);

    return (
        <>
            <TableRow className="hover:bg-muted/50">
                <TableCell className="w-[300px] pl-16">
                    <div
                        className="flex items-center w-full cursor-pointer"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        <ChevronRight
                            className={`h-4 w-4 mr-2 inline transition-transform duration-300 ease-in-out ${
                                isOpen ? "rotate-90" : "rotate-0"
                            }`}
                        />
                        {getLocationName(districtData.district, "district", districtData.district_name)}
                    </div>
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={Package}
                        value={districtData.count}
                        tooltip={`Total number of orders in ${getLocationName(districtData.district, "district", districtData.district_name)}`}
                    />
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={Package}
                        value={districtData.inactive_count || 0}
                        tooltip={`Number of draft and cancelled orders in ${getLocationName(districtData.district, "district", districtData.district_name)}`}
                    />
                </TableCell>
                <TableCell className="w-[150px] text-center">
                    <TableCellMetric
                        icon={Coins}
                        value={formatCurrency(districtData.total_amount)}
                        tooltip={`Total revenue from all orders in ${getLocationName(districtData.district, "district", districtData.district_name)}`}
                    />
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={TrendingUp}
                        value={formatCurrency(calculateAverage(districtData.total_amount, activeOrdersCount))}
                        tooltip={`Average order value in ${getLocationName(districtData.district, "district", districtData.district_name)}`}
                    />
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={Battery}
                        value={`${(districtData.total_capacity || 0).toFixed(2)} kW`}
                        tooltip={`Total capacity in ${getLocationName(districtData.district, "district", districtData.district_name)}`}
                    />
                </TableCell>
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
                            {districtData.orders.length > 0 ? (
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
                                                            ? order.sales_person.length > 17
                                                                ? order.sales_person.substring(0, 17) + "..."
                                                                : order.sales_person
                                                            : "-"}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-sm whitespace-nowrap">
                                                        {order.capacity_value ? `${order.capacity_value} kW` : "-"}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-sm whitespace-nowrap">
                                                        {order.type_of_structure || "-"}
                                                    </TableCell>
                                                    <TableCell className="py-2 text-sm whitespace-nowrap">
                                                        {formatDate(order.creation)}
                                                    </TableCell>
                                                    <TableCell className="py-1 px-1 text-sm text-right">
                                                        <div className="flex items-center justify-end gap-1 flex-wrap">
                                                            <Badge
                                                                className={`${getDepartmentColor(order.department)} text-[11px] py-0.5 px-2 whitespace-nowrap max-w-[110px]`}
                                                                variant="outline"
                                                                title={order.department || "None"}
                                                            >
                                                                {getDepartmentAcronym(order.department)}
                                                            </Badge>
                                                            <Badge
                                                                className={`${getTypeColor(order.type_of_case)} text-[11px] py-0.5 px-2 whitespace-nowrap`}
                                                                variant="outline"
                                                                title={order.type_of_case}
                                                            >
                                                                {order.type_of_case}
                                                            </Badge>
                                                            <Badge
                                                                className={`${getStatusColor(order.status)} text-[11px] py-0.5 px-2 whitespace-nowrap`}
                                                                title={order.status}
                                                            >
                                                                {order.status}
                                                            </Badge>
                                                        </div>
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>

                                    {totalPages > 1 && (
                                        <div className="flex items-center justify-between mt-3 mb-1 px-2">
                                            <div className="text-sm text-muted-foreground">
                                                Showing {indexOfFirstOrder + 1}-
                                                {Math.min(indexOfLastOrder, districtData.orders.length)} of{" "}
                                                {districtData.orders.length} orders
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={firstPage}
                                                    disabled={currentPage === 1}
                                                    title="First Page"
                                                >
                                                    <ChevronsLeft className="h-4 w-4" />
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={previousPage}
                                                    disabled={currentPage === 1}
                                                    title="Previous Page"
                                                >
                                                    <ChevronLeft className="h-4 w-4" />
                                                </Button>

                                                <span className="text-sm mx-2">
                                                    Page {currentPage} of {totalPages}
                                                </span>

                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={nextPage}
                                                    disabled={currentPage === totalPages}
                                                    title="Next Page"
                                                >
                                                    <ChevronRight className="h-4 w-4" />
                                                </Button>
                                                <Button
                                                    variant="outline"
                                                    size="icon"
                                                    className="h-7 w-7"
                                                    onClick={lastPage}
                                                    disabled={currentPage === totalPages}
                                                    title="Last Page"
                                                >
                                                    <ChevronsRight className="h-4 w-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className="px-20 py-4 text-center">
                                    <div className="flex flex-col items-center justify-center text-muted-foreground">
                                        <p>No orders found in this district</p>
                                    </div>
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
                    getERPUrl={getERPUrl}
                />
            )}
        </>
    );
};
