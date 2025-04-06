"use server";

import { createTransport } from "nodemailer";
import { RescueTeam } from "@/datas/rescueTeams";

const transport = createTransport({
  service: "gmail",
  host: "smtp.gmail.com",
  port: 465,
  secure: true,
  auth: {
    user: process.env.EMAIL,
    pass: process.env.EMAIL_PASS,
  },
});

export async function sendQuickMail({
  checkedItems,
  latitude,
  longitude,
  address,
}: {
  checkedItems: RescueTeam[];
  latitude: string;
  longitude: string;
  address: string;
}) {
  try {
    const googleMapLink = `https://www.google.com/maps/search/?api=1&query=${latitude},${longitude}`;
    const htmlContent = `
      <h2>🚨 Accident Alert</h2>
      <p><strong>Location:</strong> ${address}</p>
      <p><strong>Map Link:</strong> <a href="${googleMapLink}" target="_blank">${googleMapLink}</a></p>
    `;

    const recipients = checkedItems
  .filter((item) => item.isChecked)
  .map((item) => item.email);

console.log("Sending mail to: ", recipients);


    if (recipients.length === 0) throw new Error("No recipients selected");

    const mailResponse = await transport.sendMail({
      from: `"Accident Notifier" <${process.env.EMAIL}>`,
      to: recipients,
      subject: "🚨 Accident Alert",
      html: htmlContent,
    });

    return mailResponse;
  } catch (error) {
    console.error("Failed to send mail:", error);
    return null;
  }
}
