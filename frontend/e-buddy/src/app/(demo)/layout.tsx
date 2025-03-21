import AdminPanelLayout from "@/components/admin-panel/admin-panel-layout";
import { ThemeProvider } from '@/context/ThemeContext';


export default function DemoLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <ThemeProvider>

      <AdminPanelLayout>
        {children}
      </AdminPanelLayout>
    </ThemeProvider>
  );
}
