# Backlog

## Zielbild

`tt-auth` ist die zentrale Plattform fuer Identitaet, Zugriff, Service-Launch und spaeter gemeinsame Benutzerpraeferenzen.

## Prioritaet

1. Stabiler Login und SSO fuer alle Services
2. Benutzer- und Rechteverwaltung fuer die Plattform
3. Self-Service-Funktionen fuer Benutzer
4. Gemeinsame Praeferenzen ueber Microservices hinweg
5. Sicherheit, Audit und Betriebsreife

## Kurzfristig

- [ ] Benutzer-Registration fuer neue Plattform-Nutzer
- [ ] Invite-Flow statt offener Selbstregistrierung pruefen
- [ ] Passwort-Reset / Passwort vergessen
- [ ] bessere Fehlermeldungen bei Login und SSO
- [ ] Admin-Ansicht fuer Benutzerfreigaben pro Service

## Mittelfristig

- [ ] Benutzerprofile mit Stammdaten und Kontaktinfos
- [ ] zentrale Speicherung von Benutzerpraeferenzen
- [ ] Dark-Mode-Praferenz zentral speichern und an `tt-agenda` sowie `tt-analytics` weitergeben
- [ ] bevorzugte Sprache / Locale pro Benutzer speichern
- [ ] Service-spezifische Rollen auf Plattformebene besser modellieren
- [ ] Session-Management fuer aktive Geraete und Abmeldungen

## Sicherheit und Betrieb

- [ ] Audit-Log fuer Login, SSO-Launch und Benutzerverwaltung
- [ ] Rate Limiting fuer Login und kritische Admin-Aktionen
- [ ] MFA / zweiter Faktor evaluieren
- [ ] sauberer Prozess fuer initiale Admin-Erstellung ausserhalb von Test-Defaults
- [ ] Secrets- und Cookie-Strategie fuer Beta und Produktion haerten

## Spaeter

- [ ] externe Identity Provider evaluieren
- [ ] feinere Freigabeprozesse fuer neue Benutzer
- [ ] organisations- oder teambasierte Mandantenfaehigkeit
