"use client"

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Footer() {

    return (
        <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 mt-12">
            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col md:flex-row justify-between items-center">
                    <div className="flex items-center mb-4 md:mb-0">
                        <span className="text-lg font-bold text-gray-900 dark:text-white">
                        </span>
            </div>
            <div className="flex space-x-6">
            <a href="#" className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                <i className="fab fa-twitter"></i>
            </a>
            <a href="#" className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                <i className="fab fa-facebook"></i>
            </a>
            <a href="#" className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                <i className="fab fa-instagram"></i>
            </a>
            </div>
        </div>
        <div className="mt-4 text-center md:text-left">
            <p className="text-gray-500 dark:text-gray-400">
            </p>
        </div>
        </div>
        </footer>
    )
}