---
slug: aao-tb-mitao
---

Aao TB Mitao is a Global Fund TB programme delivered by The Indus Hospital,
Interactive Health Solutions and IRD Global, with three parts working
together. Field and facility staff use an Android app to screen, diagnose
and follow up TB patients, covering FAST, childhood TB, comorbidities, PMDT
and PET intervention types. A web platform is what the app talks to behind
the scenes, giving administrators a way to manage users, locations and
reporting; a separate call centre variant of the same platform originally
operated from IBEX Global, a major call service provider in Pakistan.
Around this core, a set of smaller integration services connect the
programme to outside systems and keep its own data warehouse up to date.

## Components

- **Mobile app**: the field and facility app. Screens, diagnoses and
  follows up TB patients across all the programme's intervention types, in
  facilities and out in the community.
- **Web platform**: the server side the mobile app talks to. Web services
  for the app, an admin interface for managing users, locations and
  reporting definitions, and a set of Pentaho report templates.
- **Call centre CRM**: nearly identical to the web platform, with a
  call-centre-specific import path added on top of the same patient,
  location and encounter records. Originally operated from IBEX Global, a
  major call service provider in Pakistan.
- **Airborne Infection Control**: a separate web and mobile pair aimed at
  controlling TB infection within health facilities themselves, rather than
  in patients. The Android app is the front end field staff use; the web
  service behind it stores the data.
- **CAD4TB integration**: connects the programme to CAD4TB, an AI-assisted
  chest X-ray reading service run by Delft Imaging's Thirona cloud,
  importing its results back into the programme's own records. The web
  module exposes an endpoint the cloud service can upload results to
  directly.
- **GxAlert integration**: pulls GeneXpert diagnostic results in from
  GxAlert, a result-relay platform for GeneXpert TB testing machines, and
  imports them into the programme's own system.
- **Data warehouse**: builds and refreshes a reporting data warehouse from
  the programme's transactional OpenMRS databases, on a schedule, for the
  reports the web platform and Pentaho templates draw on.
- **Metadata sync tool**: a small desktop tool for keeping metadata, not
  patient data, in sync between two OpenMRS instances, run on demand by an
  administrator.
- **Notifications service**: sends email, SMS and outbound call reminders
  and alerts for the programme. Started as one combined project, then split
  into a shared common library plus separate email, SMS and call modules.

## Stack

Java, GWT, Tomcat, MySQL, native Android, Pentaho, Hibernate, Maven, SQL
stored procedures, Java Swing (desktop).
