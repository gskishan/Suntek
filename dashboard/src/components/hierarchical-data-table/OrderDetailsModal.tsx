import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Battery, Building, Calendar, ExternalLink, MapPin, User, X, Users } from "lucide-react";
import { useEffect } from "react";
import { OrderDetailsModalProps } from "./types";

export const OrderDetailsModal = ({
    selectedOrder,
    closeOrderDetails,
    formatCurrency,
    formatDate,
    getStatusColor,
    getTypeColor,
    getERPUrl,
}: OrderDetailsModalProps) => {
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === "Escape" && selectedOrder) {
                closeOrderDetails();
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [selectedOrder, closeOrderDetails]);

    if (!selectedOrder) return null;

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
            onClick={(event: React.MouseEvent<HTMLDivElement>) => {
                if (event.target === event.currentTarget) {
                    closeOrderDetails();
                }
            }}
        >
            <div className="bg-white rounded-lg shadow-lg w-full max-w-4xl mx-auto overflow-hidden">
                <div className="flex items-center justify-between p-4 border-b">
                    <div>
                        <h3 className="text-lg font-semibold">Sales Order Details</h3>
                        <p className="text-sm text-gray-500">Viewing details for order {selectedOrder.name}</p>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={closeOrderDetails}
                        className="rounded-full h-8 w-8"
                    >
                        <X className="h-4 w-4" />
                    </Button>
                </div>

                <div className="p-4 space-y-4">
                    <div className="grid grid-cols-2 gap-6">
                        <div className="flex items-center gap-2 text-sm">
                            <User className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Customer:</span>
                            <span className="truncate">{selectedOrder.customer}</span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Date:</span> {formatDate(selectedOrder.creation)}
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Building className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Department:</span> {selectedOrder.department || "N/A"}
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Battery className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Capacity:</span>
                            {selectedOrder.capacity_raw ? (
                                <span title={`Extracted value: ${selectedOrder.capacity_value || "N/A"}`}>
                                    {selectedOrder.capacity_raw}
                                </span>
                            ) : (
                                "N/A"
                            )}
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Users className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Sales Person:</span>{" "}
                            {selectedOrder.sales_person
                                ? selectedOrder.sales_person.length > 17
                                    ? selectedOrder.sales_person.substring(0, 17) + "..."
                                    : selectedOrder.sales_person
                                : "-"}
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <MapPin className="h-4 w-4 text-muted-foreground" />
                            <span className="font-medium">Territory:</span> {selectedOrder.territory}
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <span className="font-medium">State:</span> {selectedOrder.state || "Unspecified"}
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <span className="font-medium">City:</span> {selectedOrder.city || "Unspecified"}
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <span className="font-medium">Structure:</span> {selectedOrder.type_of_structure || "N/A"}
                        </div>
                    </div>

                    <div className="flex justify-between items-center mt-4 pt-4 border-t">
                        <div className="flex items-center gap-4">
                            <Badge className={`${getStatusColor(selectedOrder.status)} text-[13px] py-0.5 px-3`}>
                                {selectedOrder.status}
                            </Badge>
                            <Badge className={`${getTypeColor(selectedOrder.type_of_case)} text-[13px] py-0.5 px-3`}>
                                {selectedOrder.type_of_case}
                            </Badge>
                        </div>
                        <div className="text-lg font-bold">{formatCurrency(selectedOrder.grand_total)}</div>
                    </div>
                </div>

                <div className="p-4 border-t flex justify-end gap-2">
                    <Button
                        variant="outline"
                        onClick={closeOrderDetails}
                    >
                        Close
                    </Button>
                    <Button
                        className="flex items-center gap-2"
                        onClick={() => window.open(`${getERPUrl()}/app/sales-order/${selectedOrder.name}`, "_blank")}
                    >
                        <ExternalLink className="h-4 w-4" />
                        View in ERP
                    </Button>
                </div>
            </div>
        </div>
    );
};
