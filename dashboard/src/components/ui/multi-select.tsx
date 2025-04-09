import * as React from "react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { X, Check, ChevronsUpDown, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

export interface MultiSelectOption {
    value: string;
    label: string;
}

export interface MultiSelectProps {
    values: string[];
    onValuesChange: (values: string[]) => void;
    options: MultiSelectOption[];
    placeholder?: string;
    disabled?: boolean;
}

export const MultiSelect = ({
    values = [],
    onValuesChange,
    options,
    placeholder = "Select options",
    disabled = false,
}: MultiSelectProps) => {
    const [open, setOpen] = React.useState(false);
    const [searchQuery, setSearchQuery] = React.useState("");
    const MAX_VISIBLE_BADGES = 2; // Maximum number of badges to display

    const toggleOption = React.useCallback(
        (value: string) => {
            const newValues = values.includes(value) ? values.filter((v) => v !== value) : [...values, value];
            onValuesChange(newValues);
        },
        [values, onValuesChange],
    );

    const handleRemove = React.useCallback(
        (value: string) => {
            onValuesChange(values.filter((v) => v !== value));
        },
        [values, onValuesChange],
    );

    const selectedLabels = React.useMemo(() => {
        return values
            .map((value) => options.find((option) => option.value === value))
            .filter(Boolean) as MultiSelectOption[];
    }, [values, options]);

    // Get all selected labels as a comma-separated string for the tooltip
    const allSelectedLabelsText = React.useMemo(() => {
        return selectedLabels.map((option) => option.label).join(", ");
    }, [selectedLabels]);

    const filteredOptions = React.useMemo(() => {
        if (!searchQuery) return options;
        return options.filter((option) => option.label.toLowerCase().includes(searchQuery.toLowerCase()));
    }, [options, searchQuery]);

    return (
        <Popover
            open={open}
            onOpenChange={setOpen}
        >
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    role="combobox"
                    aria-expanded={open}
                    className={cn(
                        "w-full justify-between h-9 px-3 py-2 text-left",
                        !values.length && "text-muted-foreground",
                    )}
                    disabled={disabled}
                    onClick={() => setOpen(!open)}
                >
                    <div className="flex flex-wrap gap-1 items-center overflow-hidden">
                        {selectedLabels.length > 0 ? (
                            <TooltipProvider delayDuration={300}>
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <div className="flex flex-wrap gap-1 max-w-[90%] overflow-hidden">
                                            {selectedLabels.slice(0, MAX_VISIBLE_BADGES).map((option) => (
                                                <Badge
                                                    key={option.value}
                                                    variant="secondary"
                                                    className="text-xs px-1.5 py-0.5 h-5 truncate max-w-[120px]"
                                                    onClick={(e: React.MouseEvent<HTMLDivElement>) => {
                                                        e.stopPropagation();
                                                        handleRemove(option.value);
                                                    }}
                                                >
                                                    {option.label}
                                                    <X className="ml-1 h-3 w-3 text-muted-foreground hover:text-foreground cursor-pointer" />
                                                </Badge>
                                            ))}
                                            {selectedLabels.length > MAX_VISIBLE_BADGES && (
                                                <Badge
                                                    variant="secondary"
                                                    className="text-xs px-1.5 py-0.5 h-5 bg-primary text-primary-foreground hover:bg-primary/80"
                                                >
                                                    +{selectedLabels.length - MAX_VISIBLE_BADGES}
                                                </Badge>
                                            )}
                                        </div>
                                    </TooltipTrigger>
                                    <TooltipContent
                                        side="bottom"
                                        className="max-w-xs"
                                    >
                                        <p className="text-sm">{allSelectedLabelsText}</p>
                                    </TooltipContent>
                                </Tooltip>
                            </TooltipProvider>
                        ) : (
                            <span>{placeholder}</span>
                        )}
                    </div>
                    <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                </Button>
            </PopoverTrigger>
            <PopoverContent
                className="w-full p-2"
                align="start"
                side="bottom"
                sideOffset={5}
            >
                <div className="flex items-center border-b px-3 pb-2">
                    <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
                    <Input
                        placeholder={`Search ${placeholder.toLowerCase()}...`}
                        className="h-8 bg-transparent border-none focus-visible:ring-0 focus-visible:ring-offset-0 px-0"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                    />
                </div>

                {filteredOptions.length === 0 ? (
                    <div className="py-6 text-center text-sm">No options found</div>
                ) : (
                    <ScrollArea className="h-60 overflow-auto">
                        <div className="p-1">
                            {filteredOptions.map((option) => {
                                const isSelected = values.includes(option.value);
                                return (
                                    <div
                                        key={option.value}
                                        className={cn(
                                            "relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none hover:bg-accent hover:text-accent-foreground",
                                            isSelected && "bg-accent/50",
                                        )}
                                        onClick={() => toggleOption(option.value)}
                                    >
                                        <div
                                            className={cn(
                                                "mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-primary",
                                                isSelected ? "bg-primary text-primary-foreground" : "opacity-50",
                                            )}
                                        >
                                            {isSelected && <Check className="h-3 w-3" />}
                                        </div>
                                        <span>{option.label}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </ScrollArea>
                )}
            </PopoverContent>
        </Popover>
    );
};
