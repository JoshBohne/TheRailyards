CREATE TABLE `feedback` (
	`id` text PRIMARY KEY NOT NULL,
	`message` text NOT NULL,
	`category` text NOT NULL,
	`page` text NOT NULL,
	`created_at` integer NOT NULL
);
