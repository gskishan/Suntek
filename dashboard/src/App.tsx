import { Dashboard } from "./components/Dashboard";
import { useEffect, useState } from "react";
import { useFrappeAuth } from "frappe-react-sdk";

const App = () => {
    const [userInitial, setUserInitial] = useState<string>("");
    const { currentUser, isLoading } = useFrappeAuth();

    useEffect(() => {
        if (currentUser) {
            setUserInitial(currentUser.charAt(0).toUpperCase());
        }
    }, [currentUser]);

    return (
        <div className="min-h-screen bg-background flex flex-col">
            <main className="flex-1 w-full max-w-[99%] mx-auto py-4">
                <Dashboard
                    userName={currentUser || "User"}
                    userInitial={userInitial}
                />
            </main>
        </div>
    );
};

export default App;
