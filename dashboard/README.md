# Suntek Sales Dashboard

A responsive dashboard for visualizing sales data across geographical regions and departments.

## Features

- **Multiple Views**:

    - **Location View**: Visualize sales data hierarchically by State > Territory > City > District
    - **Department View**: View sales data organized by department structure
    - **More views in development**: CRM and Activity dashboards (coming soon)

- **Advanced Filtering**:

    - Filter by date range
    - Filter by location (state, territory, city, district)
    - Filter by department
    - Filter by sales person
    - Filter by order status
    - Filter by type of case
    - Filter by type of structure
    - Quick text search with support for multiple terms and operators

- **Interactive UI**:
    - Expand/collapse hierarchical data
    - View detailed order information
    - Navigate to ERP system for more details
    - Summary statistics and charts

## Development

### Setup

```bash
# Install dependencies
cd dashboard
npm install

# Start development server
npm run dev
```

### Building for Production

```bash
# Build the dashboard
npm run build
```

This will generate the static files in the `../suntek_app/public/dashboard/` directory and copy the main HTML file to `../suntek_app/www/dashboard.html`.

## Technology Stack

- React
- TypeScript
- shadcn/ui (UI components)
- Tailwind CSS (styling)
- Frappe API (data source)

## Browser Compatibility

The dashboard is designed to work with modern browsers:

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)
