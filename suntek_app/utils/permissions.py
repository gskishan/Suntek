import frappe


def remove_duplicate_permissions():
    target_roles = [
        "Channel Partner",
        "Channel Partner Manager",
        "Sales Order Report User",
        "Solar Power Plant Manager",
    ]

    all_perms = frappe.get_all(
        "Custom DocPerm",
        fields=["name", "parent", "role", "modified"],
        filters={"role": ["in", target_roles]},
        order_by="modified desc",
    )

    print(f"Found {len(all_perms)} permissions for the specified roles")

    seen = {}
    duplicates = []
    kept = []

    for perm in all_perms:
        key = (perm.parent, perm.role)

        if key in seen:
            duplicates.append(
                {
                    "name": perm.name,
                    "parent": perm.parent,
                    "role": perm.role,
                    "modified": perm.modified,
                }
            )
        else:
            seen[key] = perm.name
            kept.append(
                {
                    "name": perm.name,
                    "parent": perm.parent,
                    "role": perm.role,
                    "modified": perm.modified,
                }
            )

    print(f"Keeping {len(kept)} unique permissions (most recent for each parent/role)")
    print(f"Found {len(duplicates)} duplicates to remove")

    by_key = {}
    for dup in duplicates:
        key = f"{dup['role']} - {dup['parent']}"
        if key not in by_key:
            by_key[key] = []
        by_key[key].append(dup)

    for key, dups in by_key.items():
        print(f"\n{key} has {len(dups)} duplicates to remove:")
        for dup in dups:
            print(f"  - {dup['name']} (modified: {dup['modified']})")

    if frappe.conf.get("developer_mode") or frappe.flags.in_patch:
        for dup in duplicates:
            try:
                frappe.delete_doc("Custom DocPerm", dup["name"])
                print(f"Deleted: {dup['name']}")
            except Exception as e:
                print(f"Error deleting {dup['name']}: {str(e)}")

        return f"Successfully removed {len(duplicates)} duplicate permissions"
    else:
        return "Run this in developer mode or as a patch to actually delete the duplicates"
