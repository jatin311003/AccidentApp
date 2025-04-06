"use client";

import React from "react";
import { useForm } from "react-hook-form";
import { Button } from "../ui/button";
import axios from "@/lib/axios";
import { LoginSchema } from "@/schemas/login-schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";
import { setCookie } from "cookies-next";

type FormData = z.infer<typeof LoginSchema>;

export default function LoginForm() {
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<FormData>({
    defaultValues: {
      email: "jatin2@gmail.com",
      password: "12345678",
    },
    resolver: zodResolver(LoginSchema),
  });

  const handleLoginSubmit = async (data: FormData) => {
    toast.loading("Logging in...", {
      id: "login",
    });

    try {
      const response = await axios.post(
        "http://127.0.0.1:8080/api/v1/auth/login",
        {
          email: data.email,
          password: data.password,
        },
        {
          withCredentials: true,
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      setCookie("token", response.data.access_token, {
        maxAge: 60 * 60 * 24, // 1 day
      });

      toast.success("Logged in successfully!", {
        id: "login",
      });

      router.push("/dashboard");
    } catch (error: any) {
      if (error.response?.data?.msg) {
        toast.error(error.response.data.msg, { id: "login" });
      } else {
        // console.error("Login error:", error);
        toast.error("An unexpected error occurred.", { id: "login" });
      }
    } finally {
      reset();
    }
  };

  return (
    <div className="sm:max-w-[460px] shadow-sm mx-auto bg-white p-5 border rounded-md">
      <h2 className="text-2xl font-bold pb-5 text-center underline">Login</h2>
      <form onSubmit={handleSubmit(handleLoginSubmit)} className="space-y-5">
        <div className="space-y-2">
          <label htmlFor="email">
            Email <span className="text-red-500">*</span>
          </label>
          <input
            type="email"
            className="w-full px-4 py-3 rounded-md border outline-none"
            autoComplete="off"
            {...register("email")}
          />
          <span className="text-sm text-red-500">
            {errors.email?.message}
          </span>
        </div>

        <div className="space-y-2">
          <label htmlFor="password">
            Password <span className="text-red-500">*</span>
          </label>
          <input
            type="password"
            className="w-full px-4 py-3 rounded-md border outline-none"
            autoComplete="off"
            {...register("password")}
          />
          <span className="text-sm text-red-500">
            {errors.password?.message}
          </span>
        </div>

        <Button
          type="submit"
          className="w-full"
          size="lg"
          disabled={isSubmitting}
        >
          {isSubmitting ? "Logging in..." : "Login"}
        </Button>
      </form>
    </div>
  );
}
