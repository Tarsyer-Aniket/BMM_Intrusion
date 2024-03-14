# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
import time

class CentroidTracker():
	def __init__(self, maxDisappeared=3, maxDistance=50, minDistance=20):
		
		self.nextObjectID = 1
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()
		self.startTime = OrderedDict()

		self.maxDisappeared = maxDisappeared
		self.maxDistance = maxDistance
		
		self.minDistance = minDistance
		self.startCentroid = OrderedDict()
		self.count=0

	def register(self, centroid):
		
		self.objects[self.nextObjectID] = centroid
		self.startCentroid[self.nextObjectID] = centroid
		self.count+=1
		self.disappeared[self.nextObjectID] = 0
		self.startTime[self.nextObjectID] = int(time.time())
		self.nextObjectID += 1

	def deregister(self, objectID):
		if int(self.startCentroid[objectID][0]-self.objects[objectID][0]) > 0:
			print('POS {}'.format(self.count))
		else:
			print('NEG {}'.format(self.count))		
		dist_ = np.linalg.norm(np.array(self.startCentroid[objectID])-np.array(self.objects[objectID]))
		print('distance = {}'.format(dist_))
		if dist_<self.minDistance:
			self.count-=1
			print('LESS THAN MIN DISTANCE')
		
		del self.objects[objectID]
		del self.disappeared[objectID]
		del self.startTime[objectID]
		del self.startCentroid[objectID]

	def update(self, rects):
		
		if len(rects) == 0:
			try:
				for objectID in self.disappeared.keys():
					self.disappeared[objectID] += 1

					
					if self.disappeared[objectID] > self.maxDisappeared:
						self.deregister(objectID)
			except:
				# camera_vsq.vsq_logger.info('Exception')
				print('..................***********************')

			return self.objects, self.startTime

		inputCentroids = np.zeros((len(rects), 2), dtype="int")

		for (i, (startX, startY, endX, endY)) in enumerate(rects):
			cX = int((startX + endX) / 2.0)
			cY = int((startY + endY) / 2.0)
			inputCentroids[i] = (cX, cY)

		if len(self.objects) == 0:
			for i in range(0, len(inputCentroids)):
				self.register(inputCentroids[i])

		else:
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())

			D = dist.cdist(np.array(objectCentroids), inputCentroids)

			rows = D.min(axis=1).argsort()

			cols = D.argmin(axis=1)[rows]

			usedRows = set()
			usedCols = set()

			for (row, col) in zip(rows, cols):
				if row in usedRows or col in usedCols:
					continue


				if D[row, col] > self.maxDistance:
						self.register(inputCentroids[col])
						usedRows.add(row)
						usedCols.add(col)
						continue

				objectID = objectIDs[row]
				self.objects[objectID] = inputCentroids[col]
				self.disappeared[objectID] = 0

				usedRows.add(row)
				usedCols.add(col)

			unusedRows = set(range(0, D.shape[0])).difference(usedRows)
			unusedCols = set(range(0, D.shape[1])).difference(usedCols)

			if D.shape[0] >= D.shape[1]:
				for row in unusedRows:
					objectID = objectIDs[row]
					self.disappeared[objectID] += 1

					if self.disappeared[objectID] > self.maxDisappeared:
						self.deregister(objectID)

			else:
				for col in unusedCols:
					self.register(inputCentroids[col])

		return self.objects, self.startTime
		#return self.objects
