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
    inactive_count?: number;
    total_capacity?: number;
    orders: SalesOrder[];
}

export interface CityData {
    city: string | null;
    total_amount: number;
    count: number;
    inactive_count?: number;
    total_capacity?: number;
    districts: DistrictData[];
}

export interface TerritoryData {
    territory: string;
    total_amount: number;
    count: number;
    inactive_count?: number;
    total_capacity?: number;
    cities: CityData[];
}

export interface StateData {
    state: string | null;
    total_amount: number;
    count: number;
    inactive_count?: number;
    total_capacity?: number;
    territories: TerritoryData[];
}

export interface DepartmentData {
    department: string | null;
    total_amount: number;
    count: number;
    inactive_count?: number;
    total_capacity?: number;
    orders: SalesOrder[];
}

export interface DepartmentTerritoryData {
    territory: string;
    total_amount: number;
    count: number;
    inactive_count?: number;
    total_capacity?: number;
    departments: DepartmentData[];
}

export interface DepartmentStateData {
    state: string | null;
    total_amount: number;
    count: number;
    inactive_count?: number;
    total_capacity?: number;
    territories: DepartmentTerritoryData[];
}

export interface HierarchicalDataTableProps {
    data: StateData[] | DepartmentStateData[];
    viewType?: "location" | "department";
}

export interface TableCellMetricProps {
    icon: React.ElementType;
    value: React.ReactNode;
    tooltip: string;
}

export interface BaseRowProps {
    getLocationName: (
        value: string | null,
        type: "state" | "city" | "district" | "territory" | "department",
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
    getERPUrl: (doctype: string, name: string) => string;
    getDepartmentColor: (department: string | null) => string;
}

export interface StateRowProps {
    stateData: StateData | DepartmentStateData;
    stateIndex: number;
    getLocationName: (
        value: string | null,
        type: "state" | "city" | "district" | "territory" | "department",
        districtName?: string | null,
    ) => string;
    formatCurrency: (value: number) => string;
    formatDate: (date: string) => string;
    calculateAverage: (total: number, count: number) => number;
    createUniqueKey: (value: string | null, prefix: string, index: number) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    registerRow: (key: string, setExpandedFn: (expanded: boolean) => void) => void;
    isFullExpansion: boolean;
    getERPUrl: (doctype: string, name: string) => string;
    getDepartmentColor: (department: string | null) => string;
    viewType?: "location" | "department";
}

export interface TerritoryRowProps {
    territoryData: TerritoryData | DepartmentTerritoryData;
    territoryIndex: number;
    getLocationName: (
        value: string | null,
        type: "state" | "city" | "district" | "territory" | "department",
        districtName?: string | null,
    ) => string;
    formatCurrency: (value: number) => string;
    formatDate: (date: string) => string;
    calculateAverage: (total: number, count: number) => number;
    createUniqueKey: (value: string | null, prefix: string, index: number) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    registerRow: (key: string, setExpandedFn: (expanded: boolean) => void) => void;
    isFullExpansion: boolean;
    getERPUrl: (doctype: string, name: string) => string;
    getDepartmentColor: (department: string | null) => string;
    viewType?: "location" | "department";
}

export interface CityRowProps extends BaseRowProps {
    cityData: CityData;
    cityIndex: number;
}

export interface DistrictRowProps extends BaseRowProps {
    districtData: DistrictData;
    districtIndex: number;
}

export interface DepartmentRowProps {
    departmentData: DepartmentData;
    departmentIndex: number;
    getLocationName: (
        value: string | null,
        type: "state" | "city" | "district" | "territory" | "department",
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
    getERPUrl: (doctype: string, name: string) => string;
    getDepartmentColor: (department: string | null) => string;
}

export interface SalesOrderRowProps {
    order: SalesOrder;
    expanded: boolean;
    toggleExpanded: () => void;
    formatCurrency: (value: number) => string;
    formatDate: (date: string) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    getERPUrl: (doctype: string, name: string) => string;
}

export interface OrderDetailsModalProps {
    selectedOrder: SalesOrder | null;
    closeOrderDetails: () => void;
    formatCurrency: (amount: number) => string;
    formatDate: (dateString: string) => string;
    getStatusColor: (status: string) => string;
    getTypeColor: (type: string) => string;
    getERPUrl: (doctype: string, name: string) => string;
}
