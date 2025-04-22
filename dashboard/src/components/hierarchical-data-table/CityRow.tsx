import { useEffect, useRef, useState } from "react";
import { Table, TableCell, TableRow, TableBody } from "@/components/ui/table";
import { ChevronRight } from "lucide-react";
import { Battery, Coins, Package, TrendingUp } from "lucide-react";
import { CityRowProps } from "./types";
import { TableCellMetric } from "./TableCellMetric";
import { DistrictRow } from "./DistrictRow";

export const CityRow = ({
    cityData,
    cityIndex,
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
}: CityRowProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const rowKey = createUniqueKey(cityData.city, "city", cityIndex);

    useRef(() => {
        registerRow(rowKey, setIsOpen);
    }).current();

    useEffect(() => {
        if (isFullExpansion) {
            setIsOpen(true);
        }
    }, [isFullExpansion]);

    const activeOrdersCount = cityData.count - cityData.inactive_count;

    return (
        <>
            <TableRow className="hover:bg-muted/50">
                <TableCell className="pl-12">
                    <div
                        className="flex items-center w-full cursor-pointer"
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        <ChevronRight
                            className={`h-4 w-4 mr-2 inline transition-transform duration-300 ease-in-out ${
                                isOpen ? "rotate-90" : "rotate-0"
                            }`}
                        />
                        {getLocationName(cityData.city, "city")}
                    </div>
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={Package}
                        value={cityData.count}
                        tooltip={`Total number of orders in ${getLocationName(cityData.city, "city")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={Package}
                        value={cityData.inactive_count || 0}
                        tooltip={`Number of draft and cancelled orders in ${getLocationName(cityData.city, "city")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={Coins}
                        value={formatCurrency(cityData.total_amount)}
                        tooltip={`Total revenue from all orders in ${getLocationName(cityData.city, "city")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={TrendingUp}
                        value={formatCurrency(calculateAverage(cityData.total_amount, activeOrdersCount))}
                        tooltip={`Average order value in ${getLocationName(cityData.city, "city")}`}
                    />
                </TableCell>
                <TableCell>
                    <TableCellMetric
                        icon={Battery}
                        value={`${cityData.total_capacity.toFixed(2)} kW`}
                        tooltip={`Total capacity in ${getLocationName(cityData.city, "city")}`}
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
                                {cityData.districts.map((districtData, districtIndex) => (
                                    <DistrictRow
                                        key={createUniqueKey(districtData.district, "district", districtIndex)}
                                        districtData={districtData}
                                        districtIndex={districtIndex}
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
