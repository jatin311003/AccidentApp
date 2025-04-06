"use client";

import React from "react";
import { useForm, SubmitHandler, FieldValues } from "react-hook-form";
import { Button } from "../ui/button";
import axios from "@/lib/axios";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";
import { setCookie } from "cookies-next";


type Props = {};

type FormData = {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
};

export default function RegisterForm({}: Props) {
  const router = useRouter();
  const {
    register,
    formState: { errors, isSubmitting },
    handleSubmit,
    reset,
  } = useForm<FormData>();

  const handleRegisterSubmit = async (data: FieldValues) => {
    if (data.password !== data.confirmPassword) {
      toast.error("Passwords do not match.");
      return;
    }

    toast("Registering...", {
      id: "register",
    });

    try {
      const response = await axios.post(
        "http://127.0.0.1:8080/api/v1/auth/register",
        {
          username: data.username,
          email: data.email,
          password: data.password,
          withCredentials: true,
        }
      );

      toast.success("Registered successfully!", {
        id: "register",
      });

      // Router redirect using replace for instant navigation
      router.replace("/auth/login");

    } catch (error: any) {
      if (error && error.response) {
        toast.error(error.response.data.msg, {
          id: "register",
        });
      } else {
        toast.error("An error occurred. Please try again later.", {
          id: "register",
        });
      }
    } finally {
      reset();
    }
  };

  return (
    <div className="sm:max-w-[460px] shadow-sm mx-auto bg-white p-5 border rounded-md">
      <h2 className="text-2xl font-bold pb-5 text-center underline">Register</h2>
      <form onSubmit={handleSubmit(handleRegisterSubmit)} className="space-y-5">
        <div className="space-y-2">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            className="w-full px-4 py-3 rounded-md border outline-none"
            {...register("username", { required: "Username is required" })}
          />
          <span className="inline-block text-sm text-red-500">{errors.username?.message}</span>
        </div>

        <div className="space-y-2">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            className="w-full px-4 py-3 rounded-md border outline-none"
            {...register("email", { required: "Email is required" })}
          />
          <span className="inline-block text-sm text-red-500">{errors.email?.message}</span>
        </div>

        <div className="space-y-2">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            className="w-full px-4 py-3 rounded-md border outline-none"
            {...register("password", { required: "Password is required" })}
          />
          <span className="inline-block text-sm text-red-500">{errors.password?.message}</span>
        </div>

        <div className="space-y-2">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            className="w-full px-4 py-3 rounded-md border outline-none"
            {...register("confirmPassword", { required: "Please confirm your password" })}
          />
          <span className="inline-block text-sm text-red-500">{errors.confirmPassword?.message}</span>
        </div>

        <Button className="w-full" size="lg">Register</Button>
      </form>
    </div>
  );
}
