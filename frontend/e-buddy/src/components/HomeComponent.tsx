// File: src/app/page.tsx
import Image from 'next/image';
import bgImage from '../assets/e-buddy__bg.png';

export const metadata = {
  title: 'E-Buddy | Your Virtual Shopping Companion',
  description:
    'Discover a seamless shopping experience with E-Buddy. Enjoy exclusive deals and a UI/UX designed with you in mind.',
};

export default function HomeComponent() {
  return (
    <main className="min-h-screen flex">
      {/* Left Column: Larger Text */}
      <div className="w-1/2 flex flex-col justify-center p-8">
        <h1 className="text-9xl font-extrabold text-white">
          <span className="text-blue-500">E</span>
          <span className="text-yellow-500">-Buddy</span>
        </h1>
        <p
          className="mt-8 text-3xl text-white font-bold leading-relaxed"
          style={{ fontFamily: 'Poppins, sans-serif' }}
        >
          Welcome to E-Buddy, your friendly shopping companion. Experience a streamlined shopping journey and exclusive offers.
        </p>

      </div>
      {/* Right Column: Image */}
      <div className="w-1/2 relative min-h-screen">
        <Image
          src={bgImage}
          alt="E-Buddy Background"
          fill
          className="object-cover"
        />
      </div>
    </main>
  );
}
