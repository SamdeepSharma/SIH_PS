import React from 'react';
import { Globe } from 'lucide-react';

const LandingPage = () => {
    return (
        <div className="min-h-screen bg-[#fcfaf8] font-serif text-[#1b140e]">
            <header className="sticky top-0 z-10 bg-[#fcfaf8] border-b border-[#f3ede7]">
                <div className="container mx-auto flex items-center justify-between px-4 py-4">
                    <div className="flex items-center gap-4">
                        <img
                            src="/Ministry_of_Law_and_Justice.svg"
                            alt="JusticeBharat logo"
                            className="h-10  "
                        />
                        <h2 className="text-2xl font-bold tracking-tight">JusticeBharat</h2>
                    </div>

                    <nav className="hidden md:flex items-center gap-8">
                        <button className="hover:text-[#e68019] transition-colors">Features</button>
                        <button className="hover:text-[#e68019] transition-colors">How it works</button>
                        <button className="hover:text-[#e68019] transition-colors">Languages</button>
                        <button className="hover:text-[#e68019] transition-colors">Sign in</button>
                        <button className="flex items-center gap-2 rounded-full bg-[#f3ede7] px-4 py-2 hover:bg-[#e68019] transition-colors">
                            <Globe size={20} />
                            <span className="hidden sm:inline">Language</span>
                        </button>
                    </nav>
                </div>
            </header>

            <main className="container mx-auto px-4 py-8">
                <section
                    className="mb-16 rounded-2xl h-[600px] bg-cover bg-center p-8 text-white"
                    style={{
                        backgroundImage: 'linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.4)), url("/supremecourt.webp")',
                    }}
                >
                    <div className="max-w-2xl  mx-auto text-down">
                        <h1 className="mb-4 text-4xl font-black leading-tight md:text-5xl">
                            Welcome to the future of commercial courts
                        </h1>
                        <p className="mb-8 text-lg">
                            We're excited to showcase how AI is transforming the legal industry
                        </p>
                        <button className="rounded-full bg-[#e68019] px-6 py-3 text-[#1b140e] font-bold hover:bg-[#f3ede7] transition-colors">
                            Contact us
                        </button>
                    </div>
                </section>



                <section className="mb-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
                    {[
                        { title: 'Features', description: 'Learn about our AI capabilities and how they can improve your legal workflow', image: 'https://cdn.usegalileo.ai/stability/aab7d1fb-1f24-4afb-8cb6-1783e91405b0.png', link: '/features' },
                        { title: 'How it works', description: 'Understand the process of integrating our AI into your legal practice', image: 'https://cdn.usegalileo.ai/stability/1569e8ba-fc68-42bd-bb80-ff9f08bd0a38.png', link: '/how-it-works' },
                        { title: 'Languages', description: 'Explore the languages our AI supports and the regions we cover', image: 'https://cdn.usegalileo.ai/stability/4cd3572e-8538-4fed-899f-2dc60f3dfc36.png', link: '/languages' },
                    ].map((item, index) => (
                        <a href={item.link} key={index} className="overflow-hidden rounded-lg bg-white shadow-lg transition-transform hover:scale-105">
                            <img src={item.image} alt={item.title} className="h-48 w-full object-cover" />
                            <div className="p-6">
                                <h3 className="mb-2 text-xl font-semibold">{item.title}</h3>
                                <p className="text-[#97734e]">{item.description}</p>
                            </div>
                        </a>
                    ))}
                </section>


                <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {[
                        'https://cdn.usegalileo.ai/stability/1dacee7e-4aed-41f0-befa-7e89cf74bd3f.png',
                        'https://cdn.usegalileo.ai/sdxl10/b9a0d8f0-6a78-48e2-a31b-05679c94732c.png',
                        'https://cdn.usegalileo.ai/sdxl10/802fb640-6cde-4708-98ac-6b783671ecd7.png',
                        'https://cdn.usegalileo.ai/sdxl10/9059775c-2835-4df2-bc23-06418a8313a9.png',
                    ].map((image, index) => (
                        <div key={index} className="aspect-[3/4] overflow-hidden rounded-lg">
                            <img src={image} alt={`Legal tool visual ${index + 1}`} className="h-full w-full object-cover transition-transform hover:scale-110" />
                        </div>
                    ))}
                </section>
            </main>

            <footer className="bg-[#f3ede7] mt-16 py-8">
                <div className="container mx-auto px-4">
                    <nav className="mb-8 flex flex-wrap justify-center gap-6">
                        {['Features', 'How it works', 'Languages', 'Sign in', 'Contact us'].map((item) => (
                            <button key={item} className="text-[#97734e] hover:text-[#e68019] transition-colors">{item}</button>
                        ))}
                    </nav>
                    <p className="text-center text-[#97734e]">© 2023 Sarvajna. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
