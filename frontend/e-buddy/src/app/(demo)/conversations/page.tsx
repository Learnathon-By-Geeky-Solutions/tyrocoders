import Link from "next/link";
import { Navbar } from "@/components/admin-panel/navbar";
import PlaceholderContent from "@/components/demo/placeholder-content";
import { ContentLayout } from "@/components/admin-panel/content-layout";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator
} from "@/components/ui/breadcrumb";

import ChatPanel from '@/components/ChatPanel';

export default function Conversations() {
  return (
      <div className="">
      <ChatPanel />
      </div>
    // <ContentLayout title="Conversations">
    //   {/* <Breadcrumb>
    //     <BreadcrumbList>
    //       <BreadcrumbItem>
    //         <BreadcrumbLink asChild>
    //           <Link href="/dashboard">Dashboard</Link>
    //         </BreadcrumbLink>
    //       </BreadcrumbItem>
    //       <BreadcrumbSeparator />
    //       <BreadcrumbItem>
    //         <BreadcrumbPage>Conversations</BreadcrumbPage>
    //       </BreadcrumbItem>
    //     </BreadcrumbList>
    //   </Breadcrumb> */}
      
        
    //     <ChatPanel />

    // </ContentLayout>
  );
}
