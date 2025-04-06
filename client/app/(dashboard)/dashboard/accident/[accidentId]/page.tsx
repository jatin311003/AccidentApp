"use client";

import GridContainer from "@/components/layouts/GridContainer";
import dynamic from "next/dynamic";
const CustomMap = dynamic(() => import("@/components/misc/CustomMap"), {
  ssr: false,
});
import React, { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { sendQuickMail } from "@/actions/quick-mail";
import { useForm } from "react-hook-form";
import { rescueTeamLists, RescueTeam } from "@/datas/rescueTeams";
import toast from "react-hot-toast";

export default function SingleAccidentPage({ params }: any) {
  const [checkedItems, setCheckedItems] = useState(rescueTeamLists);
  const [allChecked, setAllChecked] = useState(false);

  const { handleSubmit } = useForm();
  const {
    data: singleAccident,
    isLoading,
  } = useQuery({
    queryKey: ["accident", params.accidentId],
    queryFn: async () => {
      const res = await fetch(
        `http://127.0.0.1:8080/api/v1/accident/${params.accidentId}`
      );
      
      return await res.json();
    },
  });
  console.log(singleAccident)

  const handleCheckAll = () => {
    setAllChecked(!allChecked);
    const newList = rescueTeamLists.map((team) => ({
      ...team,
      isChecked: !allChecked,
    }));
    setCheckedItems(newList);
  };

  const handleCheckboxChangeFinal = (id: string) => {
    const updatedList = checkedItems.map((team) =>
      team.id === id ? { ...team, isChecked: !team.isChecked } : team
    );
    setCheckedItems(updatedList);
  };

  useEffect(() => {
    const allSelected = checkedItems.every((team) => team.isChecked);
    setAllChecked(allSelected);
  }, [checkedItems]);

  const onSubmit = async () => {
    if (!singleAccident?.data) {
      toast.error("No accident data available");
      return;
    }
    
    const { latitude, longitude, address } = singleAccident.data;
    
    try {
      const response = await sendQuickMail({
        checkedItems,
        latitude,
        longitude,
        address,
      });
      
      if (response) {
        toast.success("Mail Sent Successfully");
      } else {
        toast.error("Mail Failed");
      }
    } catch (error) {
      console.error("Error sending mail:", error);
      toast.error("Error sending mail");
    }
  };

  return (
    <section className="space-y-10 px-4 sm:px-8 py-10">
      {/* Rescue Team */}
      <fieldset className="border-2 border-dashed border-gray-300 p-6 rounded-md shadow-sm bg-white">
        <legend className="text-xl sm:text-2xl font-semibold text-gray-800 underline mb-4">
          Rescue Team
        </legend>
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="flex flex-col sm:flex-row sm:items-center gap-4"
        >
          <div className="flex flex-wrap gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                className="w-5 h-5"
                checked={allChecked}
                onChange={handleCheckAll}
              />
              <span>All</span>
            </label>
            {checkedItems.map((team, idx) => (
              <label key={idx} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  className="w-5 h-5"
                  checked={team.isChecked}
                  onChange={() => handleCheckboxChangeFinal(team.id)}
                />
                <span>{team.name}</span>
              </label>
            ))}
          </div>
          <Button
            type="submit"
            className="sm:ml-auto"
            disabled={isLoading || !singleAccident?.data}
          >
            Quick Mail
          </Button>
        </form>
      </fieldset>

      {/* Accident Details */}
      {isLoading ? (
        <div className="text-gray-600 animate-pulse">Loading accident data...</div>
      ) : (
        <>
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-800 underline mb-4">
              Accident Details
            </h2>
            <GridContainer className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {[
                { label: "Address", value: singleAccident?.data?.address },
                { label: "Latitude", value: singleAccident?.data?.latitude },
                { label: "Longitude", value: singleAccident?.data?.longitude },
                { label: "Severity", value: singleAccident?.data?.severity },
                {
                  label: "Severity Percentage",
                  value: `${singleAccident?.data?.severityInPercentage} %`,
                },
                { label: "Date", value: singleAccident?.data?.date },
              ].map((item, idx) => (
                <div
                  key={idx}
                  className="bg-white border border-gray-200 p-5 rounded-md shadow-sm"
                >
                  <h3 className="text-lg font-semibold text-gray-700 underline mb-1">
                    {item.label}
                  </h3>
                  <p className="text-gray-600 text-sm break-words">
                    {item.value}
                  </p>
                </div>
              ))}
            </GridContainer>
          </div>

          {/* Map Section */}
          <div className="space-y-4">
            <h2 className="text-xl sm:text-2xl font-bold underline">Accident Location</h2>
            {singleAccident?.data?.latitude && singleAccident?.data?.longitude && (
  <CustomMap
    latitude={parseFloat(singleAccident.data.latitude)}
    longitude={parseFloat(singleAccident.data.longitude)}
    address={singleAccident.data.address}
  />
)}

          </div>

          {/* Image Section */}
          {/* <div className="space-y-4">
            <h2 className="text-xl sm:text-2xl font-bold underline">Accident Image</h2>
            {singleAccident?.data?.image_url && (
              <Image
                src={singleAccident?.data?.image_url}
                width={1000}
                height={600}
                alt="Accident"
                className="rounded-lg shadow-md object-cover"
              />
            )}
          </div> */}
        </>
      )}
    </section>
  );
}
