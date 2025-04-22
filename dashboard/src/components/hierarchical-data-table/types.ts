export interface SalesOrder {
    name: string;
    customer: string;
    creation: string;
    type_of_case: string;
    type_of_structure?: string | null;
    status: string;
    grand_total: number;
    territory: string;
    state: string | null;
    district: string | null;
    district_name: string | null;
    city: string | null;
    department: string | null;
    capacity_raw?: string | null;
    capacity_value?: number | null;
    sales_person?: string | null;
}

export interface DistrictData {
    district: string | null;
    district_name: string | null;
    total_amount: number;
    count: number;
    inactive_count: number;
    total_capacity: number;
    orders: SalesOrder[];
}

export interface CityData {
    city: string | null;
    total_amount: number;
    count: number;
    inactive_count: number;
    total_capacity: number;
    districts: DistrictData[];
}

export interface TerritoryData {
    territory: string;
    total_amount: number;
    count: number;
    inactive_count: number;
    total_capacity: number;
    cities: CityData[];
}

export interface StateData {
    state: string | null;
    total_amount: number;
    count: number;
    inactive_count: number;
    total_capacity: number;
    territories: TerritoryData[];
}

export interface HierarchicalDataTableProps {
    data: StateData[];
}

export interface TableCellMetricProps {
    icon: React.ElementType;
    value: React.ReactNode;
    tooltip: string;
}

export interface BaseRowProps {
    getLocationName: (
        value: string | null,
        type: "state" | "city" | "district" | "territory",
        districtName?: string | null,
    ) => string;
    formatCurrency: (amount: number) => string;
    formatDate: (dateString: string) => string;
    calculateAverage: (total: number, count: number) => number;
    createUniqueKey: (value: string | null, prefix: string, index: number) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    registerRow: (key: string, setExpandedFn: (expanded: boolean) => void) => void;
    isFullExpansion: boolean;
    getERPUrl: () => string;
    getDepartmentAcronym: (department: string | null) => string;
    getDepartmentColor: (department: string | null) => string;
}

export interface StateRowProps extends BaseRowProps {
    stateData: StateData;
    stateIndex: number;
}

export interface TerritoryRowProps extends BaseRowProps {
    territoryData: TerritoryData;
    territoryIndex: number;
}

export interface CityRowProps extends BaseRowProps {
    cityData: CityData;
    cityIndex: number;
}

export interface DistrictRowProps extends BaseRowProps {
    districtData: DistrictData;
    districtIndex: number;
}

export interface OrderDetailsModalProps {
    selectedOrder: SalesOrder | null;
    closeOrderDetails: () => void;
    formatCurrency: (amount: number) => string;
    formatDate: (dateString: string) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    getERPUrl: () => string;
}
