import * as React from "react";
import { Check, ChevronsUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem } from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";

interface Location {
    name: string;
    creation: string;
    [key: string]: any;
}

interface LocationSelectProps {
    label: string;
    value?: Location | null;
    onSelect: (location: Location | null) => void;
    options?: Location[];
    displayField?: string;
}

export function LocationSelect({ label, value, onSelect, options = [], displayField = "name" }: LocationSelectProps) {
    const [open, setOpen] = React.useState(false);

    return (
        <div className="space-y-2">
            <label className="text-sm font-medium">{label}</label>
            <Popover
                open={open}
                onOpenChange={setOpen}
            >
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        role="combobox"
                        aria-expanded={open}
                        className="w-full justify-between"
                    >
                        {value ? value[displayField] : `Select ${label.toLowerCase()}...`}
                        <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0">
                    <Command>
                        <CommandInput placeholder={`Search ${label.toLowerCase()}...`} />
                        <CommandEmpty>No {label.toLowerCase()} found.</CommandEmpty>
                        <CommandGroup className="max-h-[300px] overflow-auto">
                            {options.map((option) => (
                                <CommandItem
                                    key={option.creation}
                                    value={option[displayField]}
                                    onSelect={() => {
                                        onSelect(option);
                                        setOpen(false);
                                    }}
                                >
                                    <Check
                                        className={cn(
                                            "mr-2 h-4 w-4",
                                            value?.creation === option.creation ? "opacity-100" : "opacity-0",
                                        )}
                                    />
                                    {option[displayField]}
                                </CommandItem>
                            ))}
                        </CommandGroup>
                    </Command>
                </PopoverContent>
            </Popover>
        </div>
    );
}
