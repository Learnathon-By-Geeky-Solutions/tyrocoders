import HomeComponent from "@/components/HomeComponent";

export default function Home() {
  return (
    <>
      <HomeComponent />
    </>
  );
}



// import { NextPage } from 'next'
// import Head from 'next/head'
// import Link from "next/link";
// import Image from 'next/image'
// import { ChatBubbleOvalLeftIcon, CloudArrowUpIcon, CpuChipIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

// const Home: NextPage = () => {
//   return (
//     <div className="min-h-screen bg-white">
//       <Head>
//         <title>eBuddy - AI-Powered Ecommerce Chatbot Solution</title>
//         <meta
//           name="description"
//           content="Automate customer support and boost sales with eBuddy's intelligent chatbot solution for ecommerce businesses"
//         />
//       </Head>

//       {/* Hero Section */}
//       {/* <section className="bg-blue-600 text-white py-20 text-center">
//         <h1 className="text-4xl md:text-5xl font-bold mb-4">
//           Transform Your Customer Support with an AI-Powered Chatbot
//         </h1>
//         <p className="text-lg md:text-xl mb-8">
//           eBuddy uses your ecommerce data to deliver instant, accurate
//           answers—saving time, reducing costs, and delighting customers.
//         </p>
//         <div className="space-x-4">
//           <Link href="/signup">
//             <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200">
//               Get Started Free
//             </button>
//           </Link>
//           <Link href="/demo" className="text-white underline">
//             See Demo
//           </Link>
//         </div>
//       </section> */}
      

//       {/* Key Features Grid */}
//       <section className="py-20 px-4 bg-gray-50">
//         <div className="max-w-6xl mx-auto">
//           <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
//             Why eCommerce Owners Choose eBuddy
//           </h2>
//           <div className="grid md:grid-cols-3 gap-12">
//             {features.map((feature) => (
//               <div
//                 key={feature.title}
//                 className="bg-white p-8 rounded-xl shadow-lg"
//               >
//                 <feature.icon className="h-12 w-12 text-indigo-600 mb-6" />
//                 <h3 className="text-xl font-bold mb-4">{feature.title}</h3>
//                 <p className="text-gray-600">{feature.description}</p>
//               </div>
//             ))}
//           </div>
//         </div>
//       </section>

//       {/* How It Works Section */}
//       <section className="py-20 px-4">
//         <div className="max-w-6xl mx-auto">
//           <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
//             Simple Integration, Instant Results
//           </h2>
//           <div className="flex flex-col md:flex-row gap-12 items-center">
//             <div className="flex-1 space-y-12">
//               {steps.map((step, index) => (
//                 <div key={step.title} className="flex items-start gap-6">
//                   <div className="bg-indigo-100 text-indigo-600 w-12 h-12 rounded-full flex items-center justify-center font-bold">
//                     {index + 1}
//                   </div>
//                   <div>
//                     <h3 className="text-xl font-bold mb-2">{step.title}</h3>
//                     <p className="text-gray-600">{step.description}</p>
//                   </div>
//                 </div>
//               ))}
//             </div>
//             <div className="flex-1">
//               <Image
//                 src="/integration-dashboard.png"
//                 alt="Integration Process"
//                 width={600}
//                 height={400}
//                 className="rounded-xl"
//               />
//             </div>
//           </div>
//         </div>
//       </section>

//       {/* CTA Section */}
//       <section className="bg-indigo-900 text-white py-20 px-4">
//         <div className="max-w-4xl mx-auto text-center">
//           <h2 className="text-3xl md:text-4xl font-bold mb-6">
//             Ready to Reduce Support Tickets by 70%?
//           </h2>
//           <p className="text-xl mb-8 opacity-90">
//             Join 500+ ecommerce businesses using eBuddy
//           </p>
//           <button className="bg-amber-400 text-indigo-900 px-8 py-4 rounded-full text-lg font-bold hover:bg-amber-300 transition-all">
//             Get Started Now
//           </button>
//         </div>
//       </section>
//     </div>
//   );
// }

// const features = [
//   {
//     icon: CloudArrowUpIcon,
//     title: "Easy Data Integration",
//     description: "Upload product databases, FAQs, or connect directly to your CMS - we handle the rest"
//   },
//   {
//     icon: CpuChipIcon,
//     title: "Smart AI Responses",
//     description: "Natural language processing that understands and responds like a human support agent"
//   },
//   {
//     icon: ArrowPathIcon,
//     title: "Continuous Learning",
//     description: "Automatically improves responses based on customer interactions"
//   }
// ]

// const steps = [
//   {
//     title: "Upload Your Data",
//     description: "CSV files, product feeds, or website URLs - we support multiple formats"
//   },
//   {
//     title: "Train Your Chatbot",
//     description: "Our AI analyzes your content and creates a knowledge base automatically"
//   },
//   {
//     title: "Deploy in Minutes",
//     description: "Add to your website with a simple script or use our Shopify/WooCommerce plugins"
//   }
// ]

// export default Home