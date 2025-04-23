import { useEffect, useRef, useState } from "react";
import { Table, TableCell, TableRow, TableBody } from "@/components/ui/table";
import { ChevronRight } from "lucide-react";
import { Battery, Coins, Package, TrendingUp } from "lucide-react";
import { StateRowProps } from "./types";
import { TableCellMetric } from "./TableCellMetric";
import { TerritoryRow } from "./TerritoryRow";

export const StateRow = ({
    stateData,
    stateIndex,
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
    viewType = "location",
}: StateRowProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const rowKey = createUniqueKey(stateData.state, "state", stateIndex);

    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

    useEffect(() => {
        if (isFullExpansion) {
            setIsOpen(true);
        }
    }, [isFullExpansion]);

    const activeOrdersCount = stateData.count - (stateData.inactive_count || 0);

    return (
        <>
            <TableRow className="bg-muted/30 hover:bg-muted font-medium">
                <TableCell className="w-[300px] pl-4">
                    <div
                        className="flex items-center w-full cursor-pointer"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        <ChevronRight
                            className={`h-4 w-4 mr-2 inline transition-transform duration-300 ease-in-out ${
                                isOpen ? "rotate-90" : "rotate-0"
                            }`}
                        />
                        {getLocationName(stateData.state, "state")}
                    </div>
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={Package}
                        value={stateData.count}
                        tooltip={`Total number of orders in ${getLocationName(stateData.state, "state")}`}
                    />
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={Package}
                        value={stateData.inactive_count || 0}
                        tooltip={`Number of draft and cancelled orders in ${getLocationName(stateData.state, "state")}`}
                    />
                </TableCell>
                <TableCell className="w-[150px] text-center">
                    <TableCellMetric
                        icon={Coins}
                        value={formatCurrency(stateData.total_amount)}
                        tooltip={`Total revenue from all orders in ${getLocationName(stateData.state, "state")}`}
                    />
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={TrendingUp}
                        value={formatCurrency(calculateAverage(stateData.total_amount, activeOrdersCount))}
                        tooltip={`Average order value in ${getLocationName(stateData.state, "state")}`}
                    />
                </TableCell>
                <TableCell className="w-[120px] text-center">
                    <TableCellMetric
                        icon={Battery}
                        value={`${(stateData.total_capacity || 0).toFixed(2)} kW`}
                        tooltip={`Total capacity in ${getLocationName(stateData.state, "state")}`}
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
                        <Table className="w-full">
                            <TableBody>
                                {stateData.territories.map((territoryData, territoryIndex) => (
                                    <TerritoryRow
                                        key={createUniqueKey(territoryData.territory, "territory", territoryIndex)}
                                        territoryData={territoryData}
                                        territoryIndex={territoryIndex}
                                        getLocationName={getLocationName}
                                        formatCurrency={formatCurrency}
                                        formatDate={formatDate}
                                        calculateAverage={calculateAverage}
                                        createUniqueKey={createUniqueKey}
                                        getStatusColor={getStatusColor}
                                        getTypeColor={getTypeColor}
                                        registerRow={registerRow}
                                        isFullExpansion={isFullExpansion}
                                        getERPUrl={getERPUrl}
                                        getDepartmentAcronym={getDepartmentAcronym}
                                        getDepartmentColor={getDepartmentColor}
                                        viewType={viewType}
                                    />
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </TableCell>
            </TableRow>
        </>
    );
};
