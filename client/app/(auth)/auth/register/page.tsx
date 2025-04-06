import React from "react";
import MaxWidthContainer from "@/components/layouts/MaxWidthContainer";
import RegisterForm from "@/components/auth/RegisterForm";


type Props = {};

export default function page({}: Props) {
  return (
    <MaxWidthContainer className="py-6">
      <RegisterForm />
    </MaxWidthContainer>
  );
}
