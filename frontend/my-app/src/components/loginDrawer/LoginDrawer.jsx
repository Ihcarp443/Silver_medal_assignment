"use client";

import React, { useState } from "react";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Toaster } from "@/components/ui/sonner";
import { LoaderCircle } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

// const BASE_URL = process.env.NEXT_PUBLIC_ENDPOINT || "http://50.19.164.128:8000";
const BASE_URL = process.env.NEXT_PUBLIC_ENDPOINT;
export default function LoginDrawer({ isOpen, setIsOpen }) {
  const router=useRouter()
  const [action, setAction] = useState("login");
  const [isLoading, setIsLoading] = useState(false);
  const [number, setNumber] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [errors, setErrors] = useState({
    number: false,
    password: false,
  });

const handleLogin =async()=>{
    if (!number || !password) {
      setErrors({
        number: !number,
        password: !password,
      });
      return;
    }
    if (!/^\d{10}$/.test(number)) {
      toast.error("Enter a valid 10 digit phone number");
      return;
    }
    try {
      setIsLoading(true);

      const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          phone: number,
          password,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        toast.error(data.detail || "Login failed");
        return;
      }

      localStorage.setItem("user_id", String(data.user.phone));

      toast.success("Login successful");
      router.push("/chat")
      setIsOpen(false);

    } catch (error) {
      console.log(error);
      toast.error("Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };


  const handleSignup = async () => {
    if (!number || !password || !confirmPassword) {
      toast.error("Please fill all fields");
      return;
    }
    if (!/^\d{10}$/.test(number)) {
      toast.error("Enter a valid 10 digit phone number");
      return;
    }
    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }


    try {
      setIsLoading(true);

      const res = await fetch(`${BASE_URL}/auth/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          phone: number,
          password,
        }),
      });


      const data = await res.json();


      if (!res.ok) {
        toast.error(data.detail || "Signup failed");
        return;
      }


      localStorage.setItem("user_id", data.user.id);

      toast.success("Account created successfully");

      setIsOpen(false);

    } catch (error) {
      console.log(error);
      toast.error("Something went wrong");

    } finally {
      setIsLoading(false);
    }
  };


  return (
    <Drawer open={isOpen} onOpenChange={setIsOpen}>
       <Toaster richColors position="top-center" />
      <DrawerContent>

        <div className="mx-auto w-full max-w-sm">

          <DrawerHeader>
            <DrawerTitle className="text-[#1E3A8A]font-bold">
              {action === "login" ? "Login" : "Signup"}
            </DrawerTitle>
           <DrawerDescription>
           {action === "login"
            ? "Login to continue using the application."
            : "Create an account to save your chats and preferences."}
            </DrawerDescription>
          </DrawerHeader>


          <div className="grid gap-4 p-2">
            <div className="grid gap-2">
              <Label>Phone number</Label>
              <Input
                placeholder="98******01"
                value={number}
                onChange={(e) => {
                  setNumber(e.target.value);
                  setErrors(prev => ({...prev, number: false}));
                }}
                className={errors.number ? "border-red-500" : ""}
              />
            </div>


            <div className="grid gap-2">
              <Label>Password</Label>

              <Input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setErrors(prev => ({...prev, password: false}));
                }}
                className={errors.password ? "border-red-500" : ""}
              />
            </div>


            {action === "signup" && (
              <div className="grid gap-2">
                <Label>Confirm Password</Label>

                <Input
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                   onChange={(e) => {
                  setConfirmPassword(e.target.value)
                  setErrors(prev => ({...prev, password: false}));
                  }}
                />
              </div>
            )}


            {action === "login" ? (
              <p className="text-sm">
                Don't have an account?{" "}
                <span
                  className="
                    cursor-pointer
                    text-[#0F172A]
                    hover:underline
                    transition-colors
                    duration-200
                  "
                  onClick={() => setAction("signup")}
                >
                  Signup
                </span>
              </p>
            ) : (
              <p className="text-sm">
                Already have an account?{" "}
                <span
                  className="
                    cursor-pointer
                    text-[#0F172A]
                    hover:underline
                    transition-colors
                    duration-200
                  "
                  onClick={() => setAction("login")}
                >
                  Login
                </span>
              </p>
            )}

          </div>


          <DrawerFooter>

            <Button
              className="bg-[#1E293B] hover:bg-[#0F172A]
                  text-white
                  transition-colors
                  cursor-pointer"
                  onClick={() => {
                  if (action === "login") {
                    handleLogin();
                  }else{
                    handleSignup();
                  }
                }}
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="flex gap-2 items-center">
                  {action === "login"
                    ? "Logging in"
                    : "Signing up"}

                  <LoaderCircle
                    className="animate-spin"
                    size={16}
                  />
                </span>
              ) : (
                action === "login"
                  ? "Login"
                  : "Signup"
              )}
            </Button>


            <Button
              variant="outline"
              disabled={isLoading}
              onClick={() => setIsOpen(false)}
            >
              Cancel
            </Button>

          </DrawerFooter>

        </div>

      </DrawerContent>
    </Drawer>
  );
}