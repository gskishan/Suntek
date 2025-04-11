import { Dashboard } from "./components/Dashboard";
import { useFrappeGetCall } from "frappe-react-sdk";
import { useState, useEffect } from "react";

const App = () => {
    const [userName, setUserName] = useState("User");
    const [userInitial, setUserInitial] = useState("U");

    const { data: userData } = useFrappeGetCall("frappe.auth.get_logged_user");

    const { data: userInfo } = useFrappeGetCall(
        "frappe.client.get",
        {
            doctype: "User",
            name: userData?.message,
        },
        {
            enabled: !!userData?.message,
        },
    );

    useEffect(() => {
        if (userInfo?.message) {
            const fullName = userInfo.message.full_name || userInfo.message.name || "User";
            setUserName(fullName);

            // Set initial for avatar
            const nameParts = fullName.split(" ");
            setUserInitial(nameParts[0][0]?.toUpperCase() || "U");
        }
    }, [userInfo]);

    return (
        <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 flex flex-col">
            <header className="bg-white border-b border-slate-200 shadow-sm">
                <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg overflow-hidden flex items-center justify-center">
                            <img
                                src="/app/file/ab19b34e3c"
                                alt="Suntek Logo"
                                className="w-full h-full object-contain"
                            />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold text-gray-900">Suntek Analytics</h1>
                            <p className="text-sm text-gray-500">Sales Performance Dashboard</p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <span className="text-sm text-slate-600">Welcome, {userName}</span>
                        <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center text-slate-600 text-sm">
                            {userInitial}
                        </div>
                    </div>
                </div>
            </header>
            <main className="flex-1 w-full max-w-[99%] mx-auto py-4">
                <Dashboard />
            </main>
        </div>
    );
};

export default App;
