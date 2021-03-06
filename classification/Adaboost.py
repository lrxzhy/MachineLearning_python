#!/usr/bin/python
# -*- coding:utf-8 -*-

from numpy import *

def loadSimpData():
	datMat = matrix([[1. , 2.1],
		[2.  , 1.1],
		[1.3 , 1. ],
		[1.  , 1, ],
		[2.  , 1, ]])
	classLabels = [1.0 , 1.0 , -1.0 , -1.0 , 1.0]
	return datMat , classLabels

#单层决策树生成函数
def stumpClassify(dataMatrix , dimen , threshVal , threshIneq):
	retArray = ones((shape(dataMatrix)[0] , 1))
	if threshIneq == 'It':
		retArray[dataMatrix[: , dimen] <= threshVal] = -1.0
	else:
		retArray[dataMatrix[: , dimen] > threshVal] = -1.0
	return retArray

#输入分别是样本集，分类集，和每个样本的权重
def buildStump(dataArr , classLabels , D):
	dataMatrix = mat(dataArr)
	labelMat = mat(classLabels).T
	m , n = shape(dataMatrix)
	numSteps = 10.0
	bestStump = {}
	bestClasEst = mat(zeros((m,1)))
	minError = inf 
	for i in range(n):
		rangeMin = dataMatrix[: , i].min()
		rangeMax = dataMatrix[: , i].max()
		stepSize = (rangeMax - rangeMin)/numSteps
		for j in range(-1 , int(numSteps) + 1):
			for inequal in ['It' , 'gt']:
				threshVal = (rangeMin + float(j) * stepSize)
				predictedVals = stumpClassify(dataMatrix , i , threshVal , inequal)
				errArr = mat(ones((m,1)))
				errArr[predictedVals == labelMat] = 0
				weightedError = D.T * errArr
				if weightedError < minError:
					minError = weightedError
					bestClasEst = predictedVals.copy()
					bestStump['dim'] = i
					bestStump['thresh'] = threshVal
					bestStump['ineq'] = inequal
	return bestStump , minError , bestClasEst

#基于单层决策树的AdaBoost的训练
def adaBoostTrainDS(dataArr , classLabels , numIt = 40):
	weakClassArr = []
	m = shape(dataArr)[0]
	D = mat(ones((m , 1))/m)
	aggClassEst = mat(zeros((m , 1)))
	for i in range(numIt):
		bestStump , error , classEst = buildStump(dataArr , classLabels , D)
		print 'D:' , D.T
		alpha = float(0.5 * log((1.0 - error) / max(error , 1e-16)))
		bestStump['alpha'] = alpha
		weakClassArr.append(bestStump)
		print 'classEst: ' , classEst.T
		expon = multiply(-1 * alpha * mat(classLabels).T , classEst)
		D = multiply(D , exp(expon))
		D = D/D.sum()
		aggClassEst += alpha * classEst
		print 'aggClassEst: ' , aggClassEst.T
		aggErrors = multiply(sign(aggClassEst) != mat(classLabels).T , ones((m , 1)))
		errorRate = aggErrors.sum() / m
		print 'total error: ' , errorRate , '\n'
		if errorRate == 0.0:
			break
	return weakClassArr

#分类函数 , 输入分别为测试集和多个弱分类器
def adaClassify(datToClass , classifierArr):
	dataMatrix = mat(datToClass)
	m = shape(dataMatrix)[0]
	aggClassEst = mat(zeros((m , 1)))
	for i in range(len(classifierArr)):
		classEst = stumpClassify(dataMatrix , classifierArr[i]['dim'], \
			classifierArr[i]['thresh'] , \
			classifierArr[i]['ineq'])
		aggClassEst += classifierArr[i]['alpha'] * classEst
		print aggClassEst
	return sign(aggClassEst)