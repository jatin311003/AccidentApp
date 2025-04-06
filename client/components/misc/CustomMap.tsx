"use client";

import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { Icon } from "leaflet";

type Props = {
  latitude: number;
  longitude: number;
  address?: string;
};

const mapPin = new Icon({
  iconUrl: "/assets/MapPin.png",
  iconSize: [25, 35],
});

export default function CustomMap({ latitude, longitude, address }: Props) {
  return (
    <div className="overflow-hidden h-[320px] rounded-md border-2">
      <MapContainer
        className="w-full h-full"
        center={[latitude, longitude]}
        zoom={15}
        scrollWheelZoom={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <Marker position={[latitude, longitude]} icon={mapPin}>
          <Popup>
            <div>
              <p>{address || "Accident Location"}</p>
            </div>
          </Popup>
        </Marker>
      </MapContainer>
    </div>
  );
}
