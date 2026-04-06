import { Link, useLocation } from "react-router-dom";
import { ClipboardList, TrendingUp, Lightbulb, Fingerprint } from "lucide-react";

const sidebarItems = [
  { label: "Assessment", icon: ClipboardList, path: "/dashboard" },
  { label: "Future Trends", icon: TrendingUp, path: "/history" },
  { label: "Insights", icon: Lightbulb, path: "/insights" },
  { label: "Digital Twin", icon: Fingerprint, path: "/digital-twin" },
];

const AppSidebar = () => {
  const location = useLocation();

  return (
    <aside className="w-[200px] shrink-0 border-r border-border bg-card min-h-[calc(100vh-56px)]">
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center">
            <Fingerprint className="w-4 h-4 text-primary-foreground" />
          </div>
          <div>
            <p className="text-sm font-semibold text-foreground">Guardian</p>
            <p className="text-xs text-muted-foreground">Your Digital Twin</p>
          </div>
        </div>
      </div>
      <nav className="p-3 flex flex-col gap-1">
        {sidebarItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "text-primary bg-sanctuary-blue-light"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
};

export default AppSidebar;
