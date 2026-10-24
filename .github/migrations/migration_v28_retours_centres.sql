-- Coup de Patte, migration v28 (21/10/2026) : retours des centres à l'e-mail « validez votre fiche »
-- 1. Nouvelle colonne etat (centres et CRM) : actif, en pause / suspendu, fermé, sans soins, à vérifier.
-- 2. Fiches corrigées : Pont de Gau (13), Refuge de l'Arche (53, suspendu), LPO Île-de-France (75, pas de soins),
--    Faune Alfort (référence pour 75, 77, 93, 95), LPO Auvergne (63), SOS Faune Sauvage Limousin (87),
--    et retours du 23/10 : GORNA (67), Sentinelle Nature Alsace (68), LPO Île Grande (22).
-- 3. CRM : adresses e-mail non distribuées supprimées, statut et état de chaque centre contacté, journal des échanges.
-- Rejouable sans risque. Aucune adresse e-mail n'est ajoutée sur les pages publiques.
begin;

-- 1. Colonnes ------------------------------------------------------------------------------
alter table public.centres add column if not exists etat text not null default 'actif';
alter table public.centres drop constraint if exists centres_etat_chk;
alter table public.centres add constraint centres_etat_chk check (etat in ('actif','suspendu','ferme','sans_soins'));

alter table public.crm_contacts add column if not exists etat text not null default 'actif';
alter table public.crm_contacts drop constraint if exists crm_contacts_etat_chk;
alter table public.crm_contacts add constraint crm_contacts_etat_chk check (etat in ('actif','en_pause','ferme','sans_soins','a_verifier'));

-- 2. Fiches des centres ----------------------------------------------------------------------
-- 53 Refuge de l'Arche : centre de sauvegarde suspendu (réponse du secrétariat, 21/10/2026)
update public.centres set etat='suspendu', verifie_le='2026-10-21',
  note='Activité suspendue pour raisons financières (information du centre, 21/10/2026). Fiche mise à jour dès sa réouverture.'
where id='d92e117f-d83a-4d34-803e-41474042d640';

-- 75 LPO Île-de-France : pas de centre de soins, aucun animal blessé pris en charge (Elise Fontcuberta, 21/10/2026)
update public.centres set nom='LPO Île-de-France', etat='sans_soins', verifie_le='2026-10-21',
  note='Pour l''Île-de-France, Faune Alfort (école vétérinaire d''Alfort, Maisons-Alfort) accueille les animaux sauvages en détresse.'
where id='27bc9eaf-ee63-4484-8af8-ab0bc1ec91b5';

-- 94 Faune Alfort : centre de référence pour Paris et les départements d'Île-de-France sans centre référencé
update public.centres set depts_couverts=(select array_agg(distinct d order by d) from unnest(coalesce(depts_couverts,'{}'::text[]) || array['75','77','93','95']) d),
  note=coalesce(nullif(note,''),'Centre hospitalier universitaire vétérinaire.')
where id='f8455ae0-6dd3-41e1-8cee-fa9784eef489';

-- 13 Pont de Gau : fiche validée par Marine Vannier (21/10/2026)
update public.centres set
  nom='Centre de Sauvegarde de Pont de Gau',
  tel='0490978262',
  site='https://www.parcornithologique.com/fr/l-association-2/centre-de-soins.html',
  don_url='https://www.helloasso.com/associations/association-des-amis-du-parc-ornithologique-du-pont-de-gau',
  acces='Dépôt sans rendez-vous à l''accueil du parc ornithologique de Pont de Gau (RD 570), qui transmet l''oiseau au Centre de Sauvegarde.',
  horaires='Tous les jours sauf le 25 décembre : 9 h à 18 h du 1er avril au 30 septembre, 10 h à 17 h du 1er octobre au 31 mars.',
  presentation='Structure distincte du parc ornithologique : le Centre de Sauvegarde est géré par l''Association des Amis du Parc Ornithologique de Pont de Gau.',
  valide_par_centre='2026-10-21', verifie_le='2026-10-21'
where id='0d2ad683-f057-401c-b826-2b2918d73dde';

-- 63 LPO Auvergne : réponse automatique du centre (21/10/2026)
update public.centres set
  horaires='7 j/7 de 8 h à 18 h, week-ends et jours fériés compris.',
  acces='Plus de permanence téléphonique : apporte l''animal directement au centre, 2 rue de la Gantière à Clermont-Ferrand (à côté de l''arrêt de tram Margeride).',
  si_absent='Pas de permanence téléphonique : apporte l''animal au centre aux heures d''ouverture. Pour un mammifère, contacte le centre Panse-bêtes.',
  conseils_url='https://auvergne-rhone-alpes.lpo.fr/sos-biodiversite/faune-en-detresse/',
  verifie_le='2026-10-21'
where id='4fd34f40-d789-4c1a-8bbb-83760fd79eed';

-- 87 SOS Faune Sauvage (Limousin) : réponse automatique du centre (21/10/2026)
update public.centres set
  site='https://www.sosfaunesauvage.fr/',
  don_url='https://www.sosfaunesauvage.fr/nous-aider/',
  si_absent='Pour un oiseau en difficulté, envoie un SMS avec une photo au 07 78 07 11 23 : le centre ne traite pas ces demandes par e-mail.',
  verifie_le='2026-10-21'
where id='08732f89-fefb-4093-a322-5ab20121633f';

-- Retours du 23/10/2026 ----------------------------------------------------------------------
-- 67 GORNA : fiche validée par Graziella Tenin, responsable capacitaire (23/10/2026)
update public.centres set
  tel='0388014800',
  site='https://gorna.fr/',
  don_url='https://gorna.fr/adhesion-et-don',
  accueil='Tous les oiseaux européens et les mammifères de France métropolitaine, sauf les cervidés (cerf, chevreuil), les sangliers et les espèces exotiques envahissantes (ouette d''Égypte, ragondin, raton laveur, vison d''Amérique).',
  horaires='Tous les jours de 8 h à 18 h 30 (jusqu''à 20 h de mai à septembre). Accueil des animaux aux heures d''ouverture.',
  si_absent='En dehors des horaires, garde l''animal jusqu''au lendemain matin (conseils dans l''onglet Urgence du site gorna.fr) : carton ou caisse de transport avec de l''essuie-tout au fond pour un oiseau, un linge pour un mammifère, dans une pièce tempérée, calme et sombre. Un peu d''eau à disposition, jamais de nourriture, et ne le force pas à boire.',
  valide_par_centre='2026-10-23', verifie_le='2026-10-23'
where id='599fb599-287a-4907-bf24-29b1f992a95f';

-- 68 Sentinelle Nature Alsace : fiche validée par Maude Guérin, chargée de vie associative (23/10/2026)
update public.centres set
  tel='0660103086',
  don_url='https://www.helloasso.com/associations/sentinelle-nature-alsace/formulaires/4',
  accueil='Toutes les espèces, sauf les sangliers et les cervidés.',
  horaires='Variables selon les saisons : le centre tient sa fiche Google à jour.',
  acces='Accueil sans rendez-vous. En cas d''absence, des box de dépôt sont à disposition à l''extérieur.',
  si_absent='Laisse absolument un message. Si l''animal est en danger, mets-le à l''abri dans un carton percé de trous, sans eau ni nourriture, avec une source de chaleur.',
  valide_par_centre='2026-10-23', verifie_le='2026-10-23'
where id='2121bda5-6dba-4a4b-95d2-04c7998402be';

-- 22 LPO Île Grande : fiche validée par Romain Morinière, responsable de site (23/10/2026)
update public.centres set
  nom='Centre de sauvegarde LPO de l''Île Grande',
  tel='0257631313',
  don_url='https://www.helloasso.com/associations/lpo-france/formulaires/13',
  accueil='Tous les oiseaux et les petits mammifères (jusqu''à la taille d''un lièvre). Pas de mammifères plus grands, sauf les jeunes phoques en détresse, accueillis temporairement avant leur transfert vers Océanopolis.',
  horaires='Accueil des animaux 7 j/7, de 8 h 30 à 12 h et de 14 h à 16 h.',
  acces='Appel obligatoire avant d''apporter un animal : SOS Faune sauvage Bretagne au 02 57 63 13 13.',
  si_absent='Laisse un message à SOS Faune sauvage Bretagne (02 57 63 13 13) : un bénévole rappelle dès que possible.',
  valide_par_centre='2026-10-23', verifie_le='2026-10-23'
where id='61a1e76d-6659-45a8-8ce2-4ecf711d2e36';

-- 3. CRM -------------------------------------------------------------------------------------
-- 3a. Les 41 centres qui ont reçu l'e-mail du 21/10 au matin (fiches de structure, sans prénom)
create temporary table _envoi(email text primary key, issue text) on commit drop;
insert into _envoi values
 ('contactsosfaunesauvage@gmail.com','auto'),('nicostraub@outlook.com','ok'),('csfs.pays.de.savoie@gmail.com','ok'),
 ('cliniquechene@orange.fr','ok'),('ile-de-france@lpo.fr','reponse'),('contact@hirondelle.ovh','ok'),
 ('contact@sentinelle-nature-alsace.fr','valide'),('faune-sauvage688@orange.fr','rejet'),('faunesauvage@gorna.fr','valide'),
 ('alsace.mediation@lpo.fr','ok'),('association@hegalaldia.org','ok'),('cds.auvergne@lpo.fr','auto'),
 ('nathaliebaeye@orange.fr','rejet'),('ile-grande@lpo.fr','valide'),('maraisauxoiseaux@charente-maritime.fr','ok'),
 ('fcervetti@pnr-corse.fr','ok'),('centredesoins33@lpo.fr','ok'),('contact@goupilconnexion.org','ok'),
 ('sauvequiplume@hotmail.fr','ok'),('letichodrome38@gmail.com','ok'),('centre@athenas.fr','ok'),
 ('contact@alca-torda.org','rejet'),('assolesalcides@gmail.com','ok'),('faunesauvage@oniris-nantes.fr','rejet'),
 ('apus.apuces@free.fr','ok'),('sosfaunesauvage06@gmail.com','ok'),('soinsfaunesauvagetonneins@yahoo.com','ok'),
 ('accueil@lpo-anjou.org','rejet'),('nicole.girard3@wanadoo.fr','ok'),('secretariat@refuge-arche.org','reponse'),
 ('contact@csfl.fr','ok'),('vsenvol@gmail.com','ok'),('contact@volee-de-piafs.fr','rejet'),('crsfs.torsac@orange.fr','ok'),
 ('damebl@orange.fr','ok'),('association@parcornithologique.com','reponse'),('crsfsc@orange.fr','ok'),
 ('centre.soins@cpiesudchampagne.fr','ok'),('domainedesoiseaux@wanadoo.fr','ok'),('laurent.larzillieres@free.fr','rejet'),
 ('parc.isle@casq.fr','ok');

create temporary table _cible(id uuid primary key, issue text, email text) on commit drop;
insert into _cible select c.id, e.issue, lower(c.email) from public.crm_contacts c join _envoi e on lower(c.email)=e.email
where c.prenom is null and c.typologie='centre';

-- journal : l'envoi du matin pour les 41
insert into public.crm_interactions (contact_id,date,canal,sens,objet,resume,par)
select k.id,'2026-10-21 08:15+02','email','sortant','Votre fiche sur notre guide de secours à la faune',
       'Demande de validation de la fiche (animaux accueillis, horaires, consigne si personne ne répond, page de dons) et d''un lien vers coupdepatte.eu. Anne en copie.','Vincent'
from _cible k where not exists (select 1 from public.crm_interactions i where i.contact_id=k.id and i.objet='Votre fiche sur notre guide de secours à la faune');

-- envois arrivés, sans réponse à ce jour : relance dans une semaine
update public.crm_contacts c set statut='contacte', etat='actif', prochaine_action='Relancer si pas de réponse', echeance='2026-10-28',
  notes='E-mail « validez votre fiche » envoyé le 21/10/2026.'
from _cible k where k.id=c.id and k.issue='ok' and c.statut in ('a_contacter','contacte');

-- adresses non distribuées : adresse supprimée, structure marquée « à vérifier »
insert into public.crm_interactions (contact_id,date,canal,sens,objet,resume,par)
select k.id,'2026-10-21 08:20+02','email','entrant','Message non distribué',
       case when k.email like '%alca-torda.org' then 'Le domaine de l''adresse n''existe plus. Adresse supprimée de la base.'
            when k.email like '%oniris-nantes.fr' then 'Adresse inconnue du serveur de l''école vétérinaire. Adresse supprimée de la base.'
            when k.email like '%volee-de-piafs.fr' then 'Le serveur du domaine ne répond plus : message jamais remis après 3 jours de tentatives (21 au 24/10). Adresse supprimée de la base.'
            else 'Adresse introuvable (550 5.1.1). Adresse supprimée de la base.' end,'Vincent'
from _cible k where k.issue='rejet' and not exists (select 1 from public.crm_interactions i where i.contact_id=k.id and i.objet='Message non distribué');
update public.crm_contacts c set email=null, statut='injoignable', etat='a_verifier',
  prochaine_action='Trouver une autre adresse (formulaire du site ou Facebook) et vérifier que le centre est toujours actif', echeance='2026-10-28',
  notes='Adresse e-mail invalide supprimée le 21/10/2026 (message non distribué).'
from _cible k where k.id=c.id and k.issue='rejet';

-- adresses déjà rejetées le 20/10 : Centre Nhérisson (adresse invalide) et Faune Alfort (expéditeurs extérieurs bloqués)
update public.crm_contacts set email=null, statut='injoignable', etat='a_verifier', echeance='2026-10-28',
  prochaine_action='Trouver une autre adresse (formulaire du site ou Facebook) et vérifier que le centre est toujours actif',
  notes='Adresse e-mail invalide supprimée le 21/10/2026 (message du 20/10 non distribué).'
where prenom is null and centre_id='0dc961c2-efb9-4aa1-9523-48fbd9fe2c2b';
update public.crm_contacts set email=null, statut='injoignable', etat='actif', echeance='2026-10-28',
  prochaine_action='Passer par le formulaire de Faune Alfort ou par téléphone (le serveur de l''école refuse les e-mails extérieurs)',
  notes='Adresse e-mail supprimée le 21/10/2026 : le serveur de l''école bloque les messages extérieurs. Centre de référence pour 75, 77, 93, 94 et 95 sur Coup de Patte.'
where prenom is null and centre_id='f8455ae0-6dd3-41e1-8cee-fa9784eef489';

-- réponses automatiques
insert into public.crm_interactions (contact_id,date,canal,sens,objet,resume,par)
select k.id, case when k.email like 'cds.auvergne%' then '2026-10-21 08:14+02'::timestamptz else '2026-10-21 08:03+02'::timestamptz end,
       'email','entrant','Réponse automatique',
       case when k.email like 'cds.auvergne%' then 'Ouvert 7 j/7 de 8 h à 18 h, fériés compris. Plus de permanence téléphonique (charge de travail, difficultés financières) : apporter l''animal directement, 2 rue de la Gantière à Clermont-Ferrand. Mammifères : Panse-bêtes. Fiche mise à jour.'
            else 'Animal en difficulté : SMS avec photo au 07 78 07 11 23, pas de traitement par e-mail. Fiche mise à jour.' end,'Vincent'
from _cible k where k.issue='auto' and not exists (select 1 from public.crm_interactions i where i.contact_id=k.id and i.objet='Réponse automatique');
update public.crm_contacts c set statut='contacte', etat='actif', prochaine_action='Relancer si pas de réponse personnelle', echeance='2026-10-28',
  notes='Réponse automatique reçue le 21/10/2026 ; informations reportées sur la fiche.'
from _cible k where k.id=c.id and k.issue='auto';

-- 53 Refuge de l'Arche : centre en pause
insert into public.crm_interactions (contact_id,date,canal,sens,objet,resume,par)
select k.id, x.d::timestamptz,'email', x.s, x.o, x.r,'Vincent' from _cible k,
 (values ('2026-10-21 09:01+02','entrant','Centre de sauvegarde suspendu','Activité du centre de sauvegarde suspendue pour raisons financières ; le refuge nous préviendra de sa réouverture.'),
         ('2026-10-21 20:51+02','sortant','Réponse : soutien et fiche mise à jour','La fiche indique que le centre est suspendu ; mise à jour dès la réouverture.')) x(d,s,o,r)
where k.email='secretariat@refuge-arche.org' and not exists (select 1 from public.crm_interactions i where i.contact_id=k.id and i.objet=x.o);
update public.crm_contacts set statut='inactif', etat='en_pause', prochaine_action='Vérifier si le centre de sauvegarde a rouvert', echeance='2027-01-15',
  notes='Centre de sauvegarde suspendu (raisons financières), information du secrétariat le 21/10/2026. Le refuge nous informera de la réouverture. Contact vétérinaire : veterinaire@refuge-arche.org.'
where prenom is null and lower(email)='secretariat@refuge-arche.org';

-- 75 LPO Île-de-France : pas de centre de soins
insert into public.crm_interactions (contact_id,date,canal,sens,objet,resume,par)
select k.id, x.d::timestamptz,'email', x.s, x.o, x.r,'Vincent' from _cible k,
 (values ('2026-10-21 11:50+02','entrant','Pas de centre de soins','La LPO Île-de-France n''a pas de centre de soins et ne prend aucun animal blessé. Oriente vers Faune Alfort et le réseau des centres de soins.'),
         ('2026-10-21 20:51+02','sortant','Réponse : fiche précisée','Fiche précisée : aucun animal blessé pris en charge, renvoi vers Faune Alfort.')) x(d,s,o,r)
where k.email='ile-de-france@lpo.fr' and not exists (select 1 from public.crm_interactions i where i.contact_id=k.id and i.objet=x.o);
update public.crm_contacts set organisation='LPO Île-de-France', statut='contacte', etat='sans_soins', prochaine_action=null, echeance=null,
  notes='Pas de centre de soins (réponse du 21/10/2026). Partenaire possible pour la sensibilisation du public en Île-de-France.'
where prenom is null and lower(email)='ile-de-france@lpo.fr';
insert into public.crm_contacts (typologie,organisation,prenom,nom,fonction,email,tel,dept,ville,statut,etat,centre_id,suivi_par,notes)
select 'centre','LPO Île-de-France','Elise','Fontcuberta','Responsable d''équipe Vie associative','Ile-de-france@lpo.fr','0614808792','75','Paris','contacte','sans_soins','27bc9eaf-ee63-4484-8af8-ab0bc1ec91b5'::uuid,'Vincent',
       'A répondu le 21/10/2026. Standard LPO Île-de-France : 01 53 58 58 38.'
where not exists (select 1 from public.crm_contacts where nom='Fontcuberta');

-- 13 Pont de Gau : fiche validée
insert into public.crm_interactions (contact_id,date,canal,sens,objet,resume,par)
select k.id, x.d::timestamptz,'email', x.s, x.o, x.r,'Vincent' from _cible k,
 (values ('2026-10-21 14:32+02','entrant','Informations pour la fiche','Centre de Sauvegarde distinct du parc, géré par l''Association des Amis du Parc. Dépôt sans rendez-vous à l''accueil du parc (9 h-18 h d''avril à septembre, 10 h-17 h d''octobre à mars, fermé le 25 décembre). Liste des espèces prises en charge jointe. Dons : HelloAsso et PayPal.'),
         ('2026-10-21 20:51+02','sortant','Réponse : fiche mise à jour','Remerciements ; fiche mise à jour en distinguant le Centre de Sauvegarde du parc.')) x(d,s,o,r)
where k.email='association@parcornithologique.com' and not exists (select 1 from public.crm_interactions i where i.contact_id=k.id and i.objet=x.o);
update public.crm_contacts set organisation='Centre de Sauvegarde de Pont de Gau', statut='partenaire', etat='actif',
  site='https://www.parcornithologique.com/fr/l-association-2/centre-de-soins.html',
  prochaine_action='Reporter sur la fiche la liste des espèces prises en charge (pièce jointe de leur e-mail du 21/10)', echeance='2026-10-24',
  notes='Fiche validée par le centre le 21/10/2026. Géré par l''Association des Amis du Parc Ornithologique de Pont de Gau.'
where prenom is null and lower(email)='association@parcornithologique.com';
insert into public.crm_contacts (typologie,organisation,prenom,nom,fonction,email,tel,dept,ville,statut,etat,centre_id,suivi_par,notes)
select 'centre','Centre de Sauvegarde de Pont de Gau','Marine','Vannier','Chargée de mission faune sauvage','association@parcornithologique.com','0679674477','13','Saintes-Maries-de-la-Mer','partenaire','actif','0d2ad683-f057-401c-b826-2b2918d73dde'::uuid,'Vincent',
       'A validé la fiche le 21/10/2026.'
where not exists (select 1 from public.crm_contacts where nom='Vannier');

-- 3a bis. Fiches validées le 23/10 : GORNA (67), Sentinelle Nature Alsace (68), LPO Île Grande (22)
insert into public.crm_interactions (contact_id,date,canal,sens,objet,resume,par)
select k.id, x.d::timestamptz,'email','entrant','Informations pour la fiche', x.r,'Vincent'
from _cible k join (values
 ('faunesauvage@gorna.fr','2026-10-23 10:39+02','Ravis d''apparaître sur l''application. Oiseaux européens et mammifères métropolitains, sauf cervidés, sangliers et espèces exotiques envahissantes ; ouvert 7 j/7 de 8 h à 18 h 30 (20 h de mai à septembre) ; conseils hors horaires sur gorna.fr ; page de dons.'),
 ('contact@sentinelle-nature-alsace.fr','2026-10-23 09:43+02','Toutes espèces sauf sangliers et cervidés ; horaires variables (fiche Google) ; sans rendez-vous, box de dépôt extérieures ; laisser un message ; HelloAsso. Partagera notre lien quand son site sera rétabli.'),
 ('ile-grande@lpo.fr','2026-10-23 15:42+02','Oiseaux et petits mammifères (jusqu''au lièvre), jeunes phoques en transit vers Océanopolis ; 7 j/7, 8 h 30-12 h et 14 h-16 h ; appel obligatoire à SOS Faune sauvage Bretagne (02 57 63 13 13) ; HelloAsso LPO France.')) x(e,d,r) on k.email=x.e
where not exists (select 1 from public.crm_interactions i where i.contact_id=k.id and i.objet='Informations pour la fiche');
update public.crm_contacts c set statut='partenaire', etat='actif',
  prochaine_action='Envoyer un mot de remerciement avec le lien de la fiche mise à jour', echeance='2026-10-27',
  notes='Fiche validée par le centre le 23/10/2026.'
from _cible k where k.id=c.id and k.issue='valide';
update public.crm_contacts set organisation='Centre de sauvegarde LPO de l''Île Grande', tel='0257631313' where prenom is null and lower(email)='ile-grande@lpo.fr';
insert into public.crm_contacts (typologie,organisation,prenom,nom,fonction,email,tel,dept,ville,statut,etat,centre_id,suivi_par,notes)
select v.* from (values
 ('centre','GORNA','Graziella','Tenin','Responsable capacitaire','faunesauvage@gorna.fr','0775693173','67','Neuwiller-lès-Saverne','partenaire','actif','599fb599-287a-4907-bf24-29b1f992a95f'::uuid,'Vincent','A validé la fiche le 23/10/2026. Standard : 03 88 01 48 00.'),
 ('centre','Sentinelle Nature Alsace','Maude','Guérin','Chargée de vie associative','contact@sentinelle-nature-alsace.fr','0660103086','68','Hunawihr','partenaire','actif','2121bda5-6dba-4a4b-95d2-04c7998402be'::uuid,'Vincent','A validé la fiche le 23/10/2026.'),
 ('centre','Centre de sauvegarde LPO de l''Île Grande','Romain','Morinière','Responsable de site, LPO France','romain.moriniere@lpo.fr',null,'22','Pleumeur-Bodou','partenaire','actif','61a1e76d-6659-45a8-8ce2-4ecf711d2e36'::uuid,'Vincent','A validé la fiche le 23/10/2026. Copie : elise.bidaud@lpo.fr.')
) v(typologie,organisation,prenom,nom,fonction,email,tel,dept,ville,statut,etat,centre_id,suivi_par,notes)
where not exists (select 1 from public.crm_contacts c where c.nom=v.nom and c.prenom=v.prenom);

-- 3b. Tarn, PACA, Vienne : réponses envoyées le 21/10 au matin, fiches validées
insert into public.crm_interactions (contact_id,date,canal,sens,objet,resume,par)
select c.id, x.d::timestamptz,'email','sortant','Réponse : fiche corrigée en ligne','Remerciements et lien vers la fiche corrigée, Anne en copie.','Vincent'
from public.crm_contacts c join (values ('Bourdeau','2026-10-21 08:27+02'),('Manens','2026-10-21 08:28+02'),('Aubinais','2026-10-21 08:30+02')) x(n,d) on c.nom=x.n
where not exists (select 1 from public.crm_interactions i where i.contact_id=c.id and i.objet='Réponse : fiche corrigée en ligne');
update public.crm_contacts set statut='partenaire', etat='actif', prochaine_action=null, echeance=null
where centre_id in ('690174e7-33e5-4bc6-93e2-ae47ffd98587','b8d66981-7c2c-4f31-85f7-56751fa2442b')
   or (centre_id='81101df9-d07a-46fc-a50a-e9933140c7fd' and nom is distinct from 'Manens');
update public.crm_contacts set statut='partenaire', etat='actif',
  prochaine_action='Envoyer un court texte et un visuel pour Le Courrier de l''hirondelle', echeance='2026-10-24'
where nom='Manens';

-- 3c. Aucune adresse rejetée ne doit rester ailleurs dans les bases
update public.centres set email=null
where lower(email) in (select email from _envoi where issue='rejet') or lower(email) in ('contacter@culturenature.fr','cedaf@vet-alfort.fr');

commit;

-- Contrôles
select etat, count(*) from public.centres group by 1 order by 1;
select statut, etat, count(*) from public.crm_contacts where typologie='centre' group by 1,2 order by 1,2;
select count(*) as adresses_rejetees_restantes from public.crm_contacts
where lower(email) in ('faune-sauvage688@orange.fr','nathaliebaeye@orange.fr','contact@alca-torda.org','faunesauvage@oniris-nantes.fr',
                       'accueil@lpo-anjou.org','laurent.larzillieres@free.fr','contacter@culturenature.fr','cedaf@vet-alfort.fr',
                       'contact@volee-de-piafs.fr');
