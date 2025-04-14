import { useFrappeGetDocList } from "frappe-react-sdk";
import { useState } from "react";
import { Input } from "./ui/input";

interface Territory {
    name: string;
    creation: string;
}

interface TerritoryInputProps {
    onSelect: (territory: Territory | null) => void;
    value?: Territory | null;
}

export const TerritoryInput = ({ onSelect, value }: TerritoryInputProps) => {
    const [searchTerm, setSearchTerm] = useState("");
    const [isOpen, setIsOpen] = useState(false);

    const { data, isLoading } = useFrappeGetDocList("Territory", {
        fields: ["name", "creation"],
        asDict: true,
    });

    const filteredTerritories = data?.filter((territory: Territory) =>
        territory.name.toLowerCase().includes(searchTerm.toLowerCase()),
    );

    const handleSelect = (territory: Territory) => {
        onSelect(territory);
        setIsOpen(false);
    };

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <div className="relative">
            <Input
                type="text"
                placeholder="Search territory..."
                value={searchTerm}
                onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setIsOpen(true);
                }}
                onFocus={() => setIsOpen(true)}
                className="w-full"
            />

            {isOpen && filteredTerritories && filteredTerritories.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border rounded-md shadow-lg max-h-60 overflow-auto">
                    {filteredTerritories.map((territory: Territory) => (
                        <div
                            key={territory.creation}
                            className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
                            onClick={() => handleSelect(territory)}
                        >
                            {territory.name}
                        </div>
                    ))}
                </div>
            )}

            {value && <div className="mt-2 text-sm text-gray-600">Selected: {value.name}</div>}
        </div>
    );
};
