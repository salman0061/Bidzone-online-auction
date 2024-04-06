-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
--
-- Host: localhost    Database: bidzone
-- ------------------------------------------------------
-- Server version	8.0.36

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auction_data`
--

DROP TABLE IF EXISTS `auction_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auction_data` (
  `auction_id` int NOT NULL AUTO_INCREMENT,
  `item_id` int DEFAULT NULL,
  `seller_username` varchar(255) DEFAULT NULL,
  `starting_price` int DEFAULT NULL,
  `auction_start` datetime DEFAULT NULL,
  `auction_end` datetime DEFAULT NULL,
  `status` varchar(20) DEFAULT NULL,
  `winning_bidder_username` varchar(255) DEFAULT NULL,
  `winning_bid_amount` int DEFAULT NULL,
  `auction_winner_notified` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`auction_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `auction_data_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auction_data`
--

LOCK TABLES `auction_data` WRITE;
/*!40000 ALTER TABLE `auction_data` DISABLE KEYS */;
INSERT INTO `auction_data` VALUES (5,2,'nagu',25000,'2024-03-28 16:28:28',NULL,'Completed','nagu123',27000,NULL);
/*!40000 ALTER TABLE `auction_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `items`
--

DROP TABLE IF EXISTS `items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `items` (
  `item_id` int NOT NULL AUTO_INCREMENT,
  `seller_username` varchar(255) DEFAULT NULL,
  `item_name` longtext,
  `dis` longtext NOT NULL,
  `category` enum('art','antiques','electronics','collectibles','fashion','other_category') NOT NULL,
  `starting_price` int DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Active',
  `upload_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `img_id` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`item_id`),
  KEY `fk_seller_username` (`seller_username`),
  CONSTRAINT `fk_seller_username` FOREIGN KEY (`seller_username`) REFERENCES `sellers` (`seller_username`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `items`
--

LOCK TABLES `items` WRITE;
/*!40000 ALTER TABLE `items` DISABLE KEYS */;
INSERT INTO `items` VALUES (2,'nagu','laptop','laptop windows 10','electronics',25000,'Completed','2024-03-28 07:28:47','T1tM5fI0r');
/*!40000 ALTER TABLE `items` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `orders`
--

DROP TABLE IF EXISTS `orders`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `orders` (
  `order_id` int NOT NULL AUTO_INCREMENT,
  `item_id` int NOT NULL,
  `item_name` longtext,
  `amount` int DEFAULT NULL,
  `user_name` varchar(255) DEFAULT NULL,
  `item_description` longtext,
  PRIMARY KEY (`order_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`item_id`) REFERENCES `items` (`item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `orders`
--

LOCK TABLES `orders` WRITE;
/*!40000 ALTER TABLE `orders` DISABLE KEYS */;
INSERT INTO `orders` VALUES (1,2,'laptop',27000,'nagu123','laptop windows 10');
/*!40000 ALTER TABLE `orders` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `placed_bids`
--

DROP TABLE IF EXISTS `placed_bids`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `placed_bids` (
  `bid_id` int NOT NULL AUTO_INCREMENT,
  `auction_id` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `bidder_username` varchar(255) DEFAULT NULL,
  `bid_amount` int DEFAULT NULL,
  `bid_time` datetime DEFAULT NULL,
  `current_bid` int DEFAULT NULL,
  `bid_increment` int DEFAULT NULL,
  PRIMARY KEY (`bid_id`),
  KEY `auction_id` (`auction_id`),
  KEY `item_id` (`item_id`),
  CONSTRAINT `placed_bids_ibfk_1` FOREIGN KEY (`auction_id`) REFERENCES `auction_data` (`auction_id`),
  CONSTRAINT `placed_bids_ibfk_2` FOREIGN KEY (`item_id`) REFERENCES `items` (`item_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `placed_bids`
--

LOCK TABLES `placed_bids` WRITE;
/*!40000 ALTER TABLE `placed_bids` DISABLE KEYS */;
INSERT INTO `placed_bids` VALUES (7,5,2,'nagu123',26000,'2024-03-28 16:32:08',NULL,1000),(8,5,2,'nagu123',27000,'2024-03-28 16:38:57',26000,1000);
/*!40000 ALTER TABLE `placed_bids` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sellers`
--

DROP TABLE IF EXISTS `sellers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sellers` (
  `seller_username` varchar(255) NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone_number` varchar(255) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`seller_username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone_number` (`phone_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sellers`
--

LOCK TABLES `sellers` WRITE;
/*!40000 ALTER TABLE `sellers` DISABLE KEYS */;
INSERT INTO `sellers` VALUES ('nagu','nagalakshmi@codegnan.com','78364683','vijayawada','password');
/*!40000 ALTER TABLE `sellers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `username` varchar(255) NOT NULL,
  `phone_number` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `address` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`username`),
  UNIQUE KEY `phone_number` (`phone_number`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('nagu123','7834632423','nagalakshmi@codegnan.com','vijayawada','password');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-03-28 21:03:29
